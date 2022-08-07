# This code was developed by myself using some hints from third sources like stackoverflow, w3school, python documentation and google frameworks documentation.
#
# A care taker supervisor needs to create a schedule for all the carers over a 7 day period,
# subject to the following conditions:
# Each day is divided into three 8-hour shifts every day, each shift is assigned
# to a single carer, and no carer works more than one shift. Each carer is assigned to at least three shifts during the
# 7 day period

# importing library
from ortools.sat.python import cp_model


# creating data for the example
def main():
    # Data.

    num_carers = 4
    num_shifts = 3
    num_days = 7
    all_carer = range(num_carers)
    all_shifts = range(num_shifts)
    all_days = range(num_days)

    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(c, d, s)]: carer 'c' works shift 's' on day 'd'.
    shifts = {}
    for c in all_carer:
        for d in all_days:
            for s in all_shifts:
                shifts[(c, d,
                        s)] = model.NewBoolVar('shift_n%id%is%i' % (c, d, s))  # the array define assignments for
                # this shifts to carer as shift[(c, d, s)] equals 1 if shift s is assigned to carer c on day d,
                # 0 otherwise

    # Each shift is assigned to exactly one carer in the schedule period.
    for d in all_days:
        for s in all_shifts:
            model.AddExactlyOne(shifts[(c, d, s)] for c in all_carer)  # the sum of carers assigned to the shift s
            # is 1.

    # Each carer works at most one shift per day.
    for c in all_carer:
        for d in all_days:
            model.AddAtMostOne(
                shifts[(c, d, s)] for s in all_shifts)  # the sum of shifts assigned to that carer is at most 1.

    # Distributing the shifts evenly, so that each carer works
    # min_shifts_per_carer shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of carer, some carer will
    # be assigned one more shift.

    min_shifts_per_carer = (
                                       num_shifts * num_days) // num_carers  # floor division to garantee the maximun number of complete shifts per carer
    if num_shifts * num_days % num_carers == 0:
        max_shifts_per_carer = min_shifts_per_carer
    else:
        max_shifts_per_carer = min_shifts_per_carer + 1
    for c in all_carer:
        num_shifts_worked = []
        for d in all_days:
            for s in all_shifts:
                num_shifts_worked.append(shifts[(c, d, s)])
        model.Add(min_shifts_per_carer <= sum(num_shifts_worked))
        model.Add(sum(num_shifts_worked) <= max_shifts_per_carer)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True

    class CarerPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""

        def __init__(self, shifts, num_carer, num_days, num_shifts, limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shifts = shifts
            self._num_carer = num_carer
            self._num_days = num_days
            self._num_shifts = num_shifts
            self._solution_count = 0
            self._solution_limit = limit

        def on_solution_callback(self):
            self._solution_count += 1
            print('Solution %i' % self._solution_count)
            for d in range(self._num_days):
                print('Day %i' % d)
                for n in range(self._num_carer):
                    is_working = False
                    for s in range(self._num_shifts):
                        if self.Value(self._shifts[(n, d, s)]):
                            is_working = True
                            print('  Carer %i works shift %i' % (n, s))
                    if not is_working:
                        print('  Carer {} does not work'.format(n))
            if self._solution_count >= self._solution_limit:
                print('Stop search after %i solutions' % self._solution_limit)
                self.StopSearch()

        def solution_count(self):
            return self._solution_count

    # Display the first five solutions.
    solution_limit = 5
    solution_printer = CarerPartialSolutionPrinter(shifts, num_carers,
                                                   num_days, num_shifts,
                                                   solution_limit)

    solver.Solve(model, solution_printer)

    # checking the status of the solution
    status = solver.Solve(model, solution_printer)

    # Statistics.
    print('\nStatistics')
    print('  - conflicts      : %i' % solver.NumConflicts())
    print('  - branches       : %i' % solver.NumBranches())
    print('  - wall time      : %f s' % solver.WallTime())
    print('  - solutions found: %i' % solution_printer.solution_count())
    print('  - solutions status: %s' % solver.StatusName(status))


# creating an external file in the same directory of the project
with open('solutions.txt', 'w') as external_file:
    # outputting the solutions and statistics to an external file
    file_path = 'solutions.txt'
    sys.stdout = open(file_path, 'a')
    external_file.writelines("First compilation!")
    print(cp_model.CpSolver)
    external_file.close()

if __name__ == '__main__':
    main()
