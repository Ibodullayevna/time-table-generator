"""
Automated University Timetable Generator — CSP solver (Google OR-Tools CP-SAT)
==============================================================================
Model: one Boolean variable per (group, subject, day, slot):  x = 1  <=>  the subject is taught then.

HARD constraints (zero violations - solver returns INFEASIBLE instead of breaking them):
  H1  Teacher overlap  : every professor teaches at most one group per (day, slot).
  H2  Group overlap    : every group attends at most one subject per (day, slot).
  H3  Teacher load     : total weekly hours of a professor <= max_load.
  H4  No back-to-back  : the same subject never occupies two adjacent slots of a day
                         (adjacent = not separated by a long break >= 30 min, e.g. lunch).
  H5  Credit completion: every subject gets EXACTLY `hours` slots per week (hours = credits).
  H6  Availability     : professors' unavailable (day, slot) pairs and reserved slots stay empty.
SOFT preference (objective): random weights + a small penalty for late slots ->
  a random-looking but compact week; leftover slots become the "filler" (e.g. Project Work).
Different `seed` => different valid timetable.
"""
import json, random, sys
from ortools.sat.python import cp_model

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class ScheduleError(Exception):
    pass


def hours(subject):
    """Weekly hours: explicit `hours` or, by default, 1 credit = 1 hour/week."""
    return int(subject.get("hours", subject["credits"]))


def _t(m):
    return f"{m // 60}:{m % 60:02d}"


def build_columns(cfg):
    """Ordered list of slot / break columns with clock times (used by the grid renderer)."""
    h, mi = map(int, cfg.get("start_time", "09:00").split(":"))
    cur, cols = h * 60 + mi, []
    brk = {b["after"]: b for b in cfg.get("breaks", [])}
    for i in range(cfg["slots_per_day"]):
        end = cur + int(cfg.get("slot_minutes", 50))
        cols.append({"type": "slot", "index": i, "label": f"P{i + 1}", "time": f"{_t(cur)}-{_t(end)}"})
        cur = end
        b = brk.get(i + 1)
        if b and i + 1 < cfg["slots_per_day"]:
            cols.append({"type": "break", "label": b.get("label", "BREAK"),
                         "time": f"{_t(cur)}-{_t(cur + b['minutes'])}"})
            cur += b["minutes"]
    return cols


def validate(cfg):
    """Cheap pre-checks that give humans a clear reason before the solver runs."""
    errs, D, S = [], cfg["days"], cfg["slots_per_day"]
    profs = {p["id"]: p for p in cfg["professors"]}
    load = {}
    for y in cfg["years"]:
        name = f'Year {y["year"]} {y["major"]}'
        cap = D * (S - len(y.get("reserved", [])))
        need = sum(hours(s) for s in y["subjects"])
        if need > cap:
            errs.append(f"{name}: {need} weekly hours needed but only {cap} free slots exist.")
        if not y["groups"]:
            errs.append(f"{name}: no groups defined.")
        for s in y["subjects"]:
            pid = s.get("professor_id")
            if pid not in profs:
                errs.append(f'{name}: subject "{s["title"]}" has no valid professor.')
                continue
            load[pid] = load.get(pid, 0) + hours(s) * len(y["groups"])
    for pid, l in load.items():
        if l > profs[pid]["max_load"]:
            errs.append(f'{profs[pid]["name"]}: assigned {l} h/week > max load {profs[pid]["max_load"]}.')
    return errs


def generate(cfg, seed=None, time_limit=20):
    errs = validate(cfg)
    if errs:
        raise ScheduleError("\n".join(errs))
    D, S = cfg["days"], cfg["slots_per_day"]
    rnd = random.Random(seed)
    profs = {p["id"]: p for p in cfg["professors"]}
    long_after = {b["after"] for b in cfg.get("breaks", []) if b["minutes"] >= 30}
    m = cp_model.CpModel()
    x, prof_slot, prof_all, obj, groups = {}, {}, {}, [], []

    for yi, y in enumerate(cfg["years"]):
        reserved = set(y.get("reserved", []))
        for g in y["groups"]:
            groups.append((yi, g))
            for si, s in enumerate(y["subjects"]):
                pid = s["professor_id"]
                unav = {tuple(u) for u in profs[pid].get("unavailable", [])}
                for d in range(D):
                    for t in range(S):
                        v = m.NewBoolVar(f"x_{yi}_{g}_{si}_{d}_{t}")
                        x[yi, g, si, d, t] = v
                        if t in reserved or (d, t) in unav:                       # H6
                            m.Add(v == 0)
                        prof_slot.setdefault((pid, d, t), []).append(v)
                        prof_all.setdefault(pid, []).append((v, ))
                        obj.append(rnd.randint(0, 4) * v + 3 * t * v)
                # H5 exact credit hours
                m.Add(sum(x[yi, g, si, d, t] for d in range(D) for t in range(S)) == hours(s))
                # H4 no back-to-back duplicates
                for d in range(D):
                    for t in range(S - 1):
                        if (t + 1) not in long_after:
                            m.Add(x[yi, g, si, d, t] + x[yi, g, si, d, t + 1] <= 1)
            # H2 one subject per group per slot
            for d in range(D):
                for t in range(S):
                    m.AddAtMostOne(x[yi, g, si, d, t] for si in range(len(y["subjects"])))

    for vs in prof_slot.values():                                                 # H1
        if len(vs) > 1:
            m.AddAtMostOne(vs)
    for pid, vs in prof_all.items():                                              # H3
        m.Add(sum(v[0] for v in vs) <= profs[pid]["max_load"])
    m.Minimize(sum(obj))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 8
    solver.parameters.random_seed = rnd.randint(0, 10**6)
    status = solver.Solve(m)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise ScheduleError("No conflict-free timetable exists for these inputs. Try: more slots/days, "
                            "fewer hours, higher professor max load, or fewer unavailable slots.")

    pgrid = {p["id"]: [[None] * S for _ in range(D)] for p in cfg["professors"]}
    out_groups = []
    for yi, g in groups:
        y = cfg["years"][yi]
        grid, legend = [[None] * S for _ in range(D)], []
        for si, s in enumerate(y["subjects"]):
            p = profs[s["professor_id"]]
            legend.append({"code": s.get("code", ""), "title": s["title"], "professor": p["name"],
                           "hours": hours(s), "room": y.get("room", "")})
            for d in range(D):
                for t in range(S):
                    if solver.Value(x[yi, g, si, d, t]):
                        label = f'Y{y["year"]} {y["major"]}-{g}'
                        cell = {"code": s.get("code") or s["title"], "title": s["title"], "type": s.get("type", "THEORY"),
                                "professor": p["name"], "room": y.get("room", "")}
                        grid[d][t] = cell
                        pgrid[p["id"]][d][t] = {**cell, "group": label}
        out_groups.append({"label": f'Year {y["year"]} — {y["major"]} — Group {g}',
                           "filler": y.get("filler", ""), "grid": grid, "legend": legend})
    return {
        "university": cfg.get("university", ""), "semester": cfg.get("semester", "ODD"),
        "academic_year": cfg.get("academic_year", ""), "days": DAYS[:D], "columns": build_columns(cfg),
        "groups": out_groups,
        "professors": [{"id": p["id"], "name": p["name"], "max_load": p["max_load"],
                        "load": sum(1 for r in pgrid[p["id"]] for c in r if c), "grid": pgrid[p["id"]]}
                       for p in cfg["professors"]],
    }


if __name__ == "__main__":      # CLI:  python scheduler.py sample_input.json
    res = generate(json.load(open(sys.argv[1] if len(sys.argv) > 1 else "sample_input.json")), seed=1)
    for g in res["groups"]:
        print("\n" + g["label"])
        for d, row in zip(res["days"], g["grid"]):
            print(f"{d:<10}", " | ".join((c["title"][:16] if c else g["filler"] or "-").ljust(16) for c in row))
