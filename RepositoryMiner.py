import requests
import json
from datetime import datetime
from dateutil import parser
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import string
import numpy as np
import locale


# TODO Delete debug alerts


def main():
    repo_url = "https://chromium.googlesource.com/chromium/src/+log/HEAD"
    init_commit_url = "https://chromium.googlesource.com/chromium/src/+/"

    repo_param = dict(
        pretty="full",
        format="JSON",
        n="100"
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
    # DEBUG ALERT #
    debug_list = list()

    for json_data in data_json["log"]:
        commit_url = init_commit_url + json_data["commit"]
        commit_param = dict(
            format="JSON"
        )

        commit_response = requests.get(commit_url, commit_param)
        commit_data_json = json.loads(commit_response.text.replace(")]}'\n", ""))

        date_obj = parser.parse(commit_data_json["author"]["time"])
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
    # print(dev_matrix.shape)
    # print(dev_matrix)

    labels = {}
    G = nx.Graph()
    for i in range(0,dev_matrix.shape[1]):
        G.add_node(i)

    for node in G.nodes():
        labels[node] = developers[node].strip("@chromium.org")

    L = list()
    for i in range(0, dev_matrix.shape[0]):
        for j in range(0, dev_matrix.shape[1]):
            if dev_matrix.item(i-1,j-1) == 1:
                L.append(j)
        for item1 in range(len(L)):
            for item2 in range(len(L)):
                G.add_edge(item1, item2)
        del L[:]

    pos=nx.spring_layout(G)
    nx.draw(G, with_labels=False)
    nx.draw_networkx_labels(G,pos,labels,font_size=16,font_color='r')
    plt.show()

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
