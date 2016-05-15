################################
# Oğuz Kerem Tural / 150130125 #
# Umut Can Özyar / 150130022   #
################################
import requests
import json
from dateutil import parser
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import operator


def main():
    # For larger dataset program may take long time.
    # For 94000 commit, it takes approximately 1 hour 15 minutes.
    # Program utilizes Gitiles API provided by Google to get git logs.

    # Repository log URL for API
    repo_url = "https://chromium.googlesource.com/chromium/src/+log/HEAD"

    # Initial commit URL for API
    init_commit_url = "https://chromium.googlesource.com/chromium/src/+/"

    # n is page size, 8000 page size equals 1 month data approximately.
    # Between 15-05-2016 and 07-04-2016. Contain nearly 94000 commits.
    repo_param = dict(
        pretty="full",
        format="JSON",  # Format for data type, it should be JSON.
        n="8000"        # n is page size. For 8000 it displays nearly 1 month of data.
    )

    # Request JSON log data from Gitiles API
    data_response = requests.get(repo_url, repo_param)
    data_json = json.loads(data_response.text.replace(")]}'\n", ""))

    developer_mail_to_name = dict()
    developer_commit_count = dict()
    developer_commit_frequency = dict()

    commit_dates = list()
    top_developer = list()
    developers = list()

    # File paths are dumped from git logs in order to ease development.
    # Gitiles does not provide useful API to get file paths.
    # Instead it provides master tree set which is needed to be traversed.
    # Using file dump is easier, and more reliable.
    print("Getting file list...")
    path_list = get_file_paths()

    print("Getting developer list...")

    # Developer list.
    for json_data in data_json["log"]:
        if json_data["author"]["email"] not in developers:
            developers.append(json_data["author"]["email"])

    # Length of i and j for matrix.
    i = len(path_list)
    j = len(developers)

    dev_matrix = np.zeros((i, j))

    # Parsing JSON data provided by API. In order to get which files are committed,
    # we need to get commit details using API. Therefore it needs to do another request.
    print("Parsing commits...")
    print("Warning: Program may seem frozen while parsing, but it is not!")
    print("It just needs time, and some love...")
    total_commits = 0
    for json_data in data_json["log"]:
        commit_url = init_commit_url + json_data["commit"]
        commit_param = dict(
            format="JSON"
        )

        commit_response = requests.get(commit_url, commit_param)
        commit_data_json = json.loads(commit_response.text.replace(")]}'\n", ""))

        # Date list for commits.
        date_obj = parser.parse(commit_data_json["author"]["time"])
        commit_dates.append(date_obj)

        developer_mail_to_name[commit_data_json["author"]["email"]] = commit_data_json["author"]["name"]

        if commit_data_json["author"]["email"] not in developer_commit_count.keys():
            developer_commit_count[commit_data_json["author"]["email"]] = 0

        # Developer-file matrix.
        for diff in commit_data_json["tree_diff"]:
            if (diff["new_path"] + "\n") in path_list and commit_data_json["author"]["email"] in developers:
                i = path_list.index(diff["new_path"] + "\n")
                j = developers.index(commit_data_json["author"]["email"])
                dev_matrix[i][j] = 1

            # Developer commit count contains for each developer how many files are committed in given period.
            developer_commit_count[commit_data_json["author"]["email"]] += 1
            total_commits += 1
    print("Parsed", total_commits, "commits successfully!")

    # For top developers list, we have sorted developers by their commit counts. Then we took developers,
    # whose commits' sum equals 80% of totals in total.
    print("Identifying top developers...")
    sorted_x = sorted(developer_commit_count.items(), key=operator.itemgetter(1), reverse=True)

    eighty = total_commits * 80 / 100
    tita = 0
    count = 0

    for sorted_dev in sorted_x:
        top_developer.append(sorted_dev[0])
        tita = tita + sorted_dev[1]
        count += 1
        if tita >= eighty:
            break

    print("Drawing commit-developer graph...")
    labels = {}
    graph = nx.Graph()
    node_index = 0
    for i in range(0, dev_matrix.shape[1]):
        if developers[i] in top_developer:
            graph.add_node(node_index)
            node_index += 1

    for node in graph.nodes():
        labels[node] = developers[node].replace("@chromium.org", "")

    print(dev_matrix.shape[0], dev_matrix.shape[1])
    graph_list = list()
    for i in range(0, dev_matrix.shape[0]):
        for j in range(0, dev_matrix.shape[1]):
                if dev_matrix[i][j] == 1:
                    if developers[j] in top_developer:
                        graph_list.append(j)
        for item1 in range(len(graph_list)):
            for item2 in range(len(graph_list)):
                graph.add_edge(item1, item2)
        del graph_list[:]

    pos = nx.spring_layout(graph)

    nx.draw_networkx_nodes(graph, pos, node_color='r', node_size=50, alpha=0.8)
    nx.draw_networkx_edges(graph, pos, width=1.0, alpha=0.5)
    nx.draw_networkx_labels(graph, pos, labels, font_size=11, font_color='black')
    plt.savefig("dev_commit_relation_graph.pdf")
    # To show graph #
    plt.show()

    end = commit_dates[0]
    print("Commits starting at: ", commit_dates[-1], "| ending at:", commit_dates[0])
    start = commit_dates[-1]
    date_spawn = end - start

    plt.clf()
    print("Drawing commit-developer chart...")
    plt.bar(range(len(developer_commit_count)), developer_commit_count.values(), align="center")
    plt.xticks(range(len(developer_commit_count)), developer_commit_count.keys(), rotation="vertical", fontsize=8)
    plt.title("Commits per developer")
    plt.ylabel("Commits")
    plt.subplots_adjust(bottom=0.30)
    plt.savefig("developer_commit_chart.pdf")
    # To show plot #
    plt.show()

    print("Drawing commit-top developer chart...")
    top_dev_chart_list = dict()
    for dev in developer_commit_count:
        if dev in top_developer:
            top_dev_chart_list[dev] = developer_commit_count[dev]

    plt.clf()
    plt.bar(range(len(top_dev_chart_list)), top_dev_chart_list.values(), align="center")
    plt.xticks(range(len(top_dev_chart_list)), top_dev_chart_list.keys(), rotation="vertical", fontsize=8)
    plt.title("Commits per developer")
    plt.ylabel("Commits")
    plt.subplots_adjust(bottom=0.30)
    plt.savefig("top_developer_commit_chart.pdf")
    # To show plot #
    plt.show()

    # For commit frequency, we have calculated commit/hour ratio.
    for dev in developer_commit_count:
        developer_commit_frequency[dev] = developer_commit_count[dev] / (date_spawn.total_seconds() / 3600.0)

    plt.clf()
    plt.bar(range(len(developer_commit_frequency)), developer_commit_frequency.values(), align="center")
    plt.xticks(range(len(developer_commit_frequency)), developer_commit_frequency.keys(), rotation="vertical", fontsize=8)
    plt.title("Commit frequency per developer")
    plt.ylabel("Commits per hour")
    plt.subplots_adjust(bottom=0.30)
    plt.savefig("top_developer_commit_chart.pdf")
    # To show plot #
    plt.show()

    print(developer_commit_frequency)
    print(top_developer)


def get_file_paths():
    file_path_data = open("file_paths.txt", "r")
    path_list = list()
    for line in file_path_data:
        line.strip("\n")
        path_list.append(line)

    return path_list

if __name__ == '__main__':
    main()
