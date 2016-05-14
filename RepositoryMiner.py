import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# TODO Delete debug alerts


def main():
    repo_url = "https://chromium.googlesource.com/chromium/src/+log/HEAD"
    init_commit_url = "https://chromium.googlesource.com/chromium/src/+/"

    repo_param = dict(
        pretty="full",
        format="JSON",
        n="10"
    )

    data_response = requests.get(repo_url, repo_param)
    data_json = json.loads(data_response.text.replace(")]}'\n", ""))

    developer_mail_to_name = dict()
    developer_commit_count = dict()
    developer_commit_frequency = dict()

    commit_dates = list()
    top_developer = list()
    developers = list()

    path_list = get_file_paths()

    i = 1
    total_commits = 0

    for json_data in data_json["log"]:
        developers.append(json_data["author"]["email"])

    i = len(path_list)
    j = len(developers)

    dev_matrix = np.zeros((i, j))
    debug_list = list()
    for json_data in data_json["log"]:
        commit_url = init_commit_url + json_data["commit"]
        commit_param = dict(
            format="JSON"
        )

        commit_response = requests.get(commit_url, commit_param)
        commit_data_json = json.loads(commit_response.text.replace(")]}'\n", ""))

        date_obj = datetime.strptime(commit_data_json["author"]["time"], "%c")
        commit_dates.append(date_obj)

        # DEBUG ALERT #
        # print(commit_data_json["author"]["time"])
        developer_mail_to_name[commit_data_json["author"]["email"]] = commit_data_json["author"]["name"]

        if commit_data_json["author"]["email"] not in developer_commit_count.keys():
            developer_commit_count[commit_data_json["author"]["email"]] = 0

        for diff in commit_data_json["tree_diff"]:
            if (diff["new_path"] + "\n") in path_list and commit_data_json["author"]["email"] in developers:
                i = path_list.index(diff["new_path"] + "\n")
                j = developers.index(commit_data_json["author"]["email"])
                dev_matrix[i][j] = 1

                # DEBUG ALERT #
                # print(i, j)
                debug_list.append((i, j))

            developer_commit_count[commit_data_json["author"]["email"]] += 1
            total_commits += 1

        i += 1

    # DEBUG ALERT #
    di, dj = debug_list[0]
    print(dev_matrix[di][dj])

    end = commit_dates[0]
    start = commit_dates[-1]
    date_spawn = end - start

    plt.bar(range(len(developer_commit_count)), developer_commit_count.values(), align="center")
    plt.xticks(range(len(developer_commit_count)), developer_commit_count.keys(), rotation="vertical")
    plt.title("Commits per developer")
    plt.ylabel("Commits")
    plt.subplots_adjust(bottom=0.30)

    # To show plot #
    # plt.show()

    for dev in developer_commit_count:
        commit_count = developer_commit_count[dev]
        commit_ratio = (commit_count / total_commits) * 100

        developer_commit_frequency[dev] = (date_spawn.total_seconds() / 3600.0) / developer_commit_count[dev]

        if commit_ratio > 79:
            top_developer.append(dev)

    print(developer_commit_frequency)
    print(top_developer)

# DEBUG ALERT #
# print(developer_mail_to_name, developer_commit_count)


def get_file_paths():
    file_path_data = open("file_paths.txt", "r")
    path_list = list()
    for line in file_path_data:
        line.strip("\n")
        path_list.append(line)

    return path_list

if __name__ == '__main__':
    main()
