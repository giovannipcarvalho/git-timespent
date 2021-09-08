import argparse
import subprocess
from collections import defaultdict


def parse_args():
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("repo", nargs="?", default=".", help="Path to git repositiory.")
    ap.add_argument(
        "--session_split",
        "-s",
        default=30 * 60,
        type=int,
        help="Time between commits to split sessions (in seconds). Default is 30min",
    )
    ap.add_argument(
        "--granularity",
        "-g",
        default=2,
        type=int,
        help="Granularity at which to display total contribution time (1-5).",
    )
    return ap.parse_args()


def main(args):
    # get history
    history = parse_git_history(args.repo)

    # separate by author
    author_contributions = group_by_author(history)

    data = []
    for author, contributions in author_contributions.items():
        sessions = split_sessions(contributions, args.session_split)
        total_time = estimate_total_time(sessions)
        time_str = format_time(total_time, args.granularity)

        data.append((author, time_str, total_time))

    # sort by total time
    data.sort(reverse=True, key=lambda x: x[2])

    for row in data:
        author, time_str, _ = row
        # seasonal contributors might have empty time_str
        print(f"{author[:20]:20} {time_str:>10}")


def parse_git_history(src_dir="."):
    # timestamp | author
    cmd = "git log --all --format='format:%at|%an'"

    output = subprocess.check_output(cmd, cwd=src_dir, shell=True).decode("utf-8")

    history = []
    for line in output.split("\n"):
        timestamp, author = line.split("|")
        history.append((int(timestamp), author))

    return history


def group_by_author(git_history):
    author_contributions = defaultdict(list)

    for timestamp, author in git_history:
        author_contributions[author].append(timestamp)

    return author_contributions


def split_sessions(timestamps, session_split=30 * 60):
    sessions = []

    session = []
    for t in sorted(timestamps):
        if session and t - session[-1] > session_split:
            sessions.append(session)
            session = []

        session.append(t)
    else:
        if session:
            sessions.append(session)

    return sessions


def compute_avg_time_between_commits(sessions):
    time_between_commits = []

    for session in sessions:
        if not len(session) > 1:
            continue

        for a, b in zip(session[:-1], session[1:]):
            time_between_commits.append(abs(a - b))

    # TODO error-handle repos with only single commits sessions
    return sum(time_between_commits) / len(time_between_commits)


def estimate_session_duration(session):
    # lone commit sessions will have 0 estimated duration. this is dealt with
    # by adding the average time between commits to the first commit of each
    # session
    return session[-1] - session[0]


def estimate_total_time(sessions):
    avg_time_between_commits = compute_avg_time_between_commits(sessions)

    session_durations = [estimate_session_duration(s) for s in sessions]

    total_duration = sum(session_durations)
    session_start_compensation = avg_time_between_commits * len(sessions)

    return total_duration + session_start_compensation


def format_time(seconds, granularity=2):
    "borrowed from https://stackoverflow.com/a/24542445"
    intervals = (
        ("w", 604800),  # 60 * 60 * 24 * 7
        ("d", 86400),  # 60 * 60 * 24
        ("h", 3600),  # 60 * 60
        ("m", 60),
        ("s", 1),
    )

    result = []

    for name, count in intervals:
        value = int(seconds // count)

        if value:
            seconds -= value * count

            result.append(f"{value}{name}")
    return "".join(result[:granularity])


if __name__ == "__main__":
    main(parse_args())
