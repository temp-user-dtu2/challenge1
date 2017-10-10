import sys, re

S = []
boundaries = []
for i in range(1, len(sys.argv) - 1):
    if i % 2 == 1:
        S.append(sys.argv[i].replace("\"", ""))
    else:
        bound_list = sys.argv[i].replace("[", "").replace("]", "").split(",")
        bound_list = list(map(int, bound_list))
        boundaries.append((bound_list[0], bound_list[1]))

found_pos_and_size = []
seek_pos = -1
with open("index.txt", 'r', encoding="utf-8") as index_file:
    pattern = re.compile("^" + sys.argv[len(sys.argv) - 1] + ":")
    for line in index_file:
        if pattern.match(line):
            seek_pos, size = map(int, line.split(":")[-2:])
            found_pos_and_size.append((seek_pos, size))

if seek_pos < 0:
    print("No article found")
    exit(1)


def get_search_range(line, Sbeg, Send, a, b):
    found_positions = [m.start() for m in re.finditer('(?=' + Sbeg + ')', line)]
    intervals = []
    for pos in found_positions:
        beg = pos + len(Sbeg) + a
        end = pos + len(Sbeg) + b + len(Send)
        intervals.append((beg, end))
    return intervals

def find_sentences(line, S, boundaries):
    intervals = [(0, line)] # first value is the offset from the line
    start_position = 0
    end_positions = []
    for i in range(len(boundaries)):
        a, b = boundaries[i]
        new_intervals = []
        for j in range(len(intervals)):
            valid_intervals = []
            checked_intervals = get_search_range(intervals[j][1], S[i], S[i+1], a, b)
            for n in range(len(checked_intervals)):
                beg, end = checked_intervals[n]
                found_pos = line[intervals[j][0] + beg:intervals[j][0] + end].find(S[i+1])
                if found_pos != -1: # next word was found
                    valid_intervals.append((intervals[j][0], checked_intervals[n]))
                    if i == len(boundaries) - 1:
                        found_positions = [m.start() + intervals[j][0] + beg for m in re.finditer('(?=' + S[i+1] + ')', line[intervals[j][0] + beg:intervals[j][0] + end])]
                        end_positions = end_positions + found_positions
            new_intervals = new_intervals + [(inter[0] + offset, line[offset + inter[0]:offset + inter[1]]) for offset, inter in valid_intervals]
        if not new_intervals:
            break
        else:
            intervals = new_intervals
    else:
        found_intervals = []
        for end in end_positions:
            end_position = end + len(S[len(boundaries)])
            found_intervals.append((start_position, end_position))
        unique_intervals = set(found_intervals)
        return True, list(unique_intervals)
    return False, []

expression = ""
for i in range(len(S) - 1):
    expression = expression + S[i] + '.{' + str(boundaries[i][0]) + ',' + str(boundaries[i][1]) + '}'
expression = expression + S[len(S) - 1]

with open("database.txt", 'rb') as db:
    solutions = []
    for pos, size in found_pos_and_size:
        db.seek(pos)
        article = str(db.read(size))

        indices = [m.span() for m in re.finditer(expression, article)]

        for i in range(len(indices)):
            found, intervals = find_sentences(article[indices[i][0]:indices[i][1]], S, boundaries)
            if found:
                for start, end in intervals:
                    solutions.append(article[indices[i][0] + start:indices[i][0] + end].encode(sys.stdout.encoding, errors='replace'))
    print(len(solutions))
    for solution in solutions:
            print(solution)

    

