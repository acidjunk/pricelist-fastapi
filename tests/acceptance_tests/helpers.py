from deepdiff import DeepDiff


def get_difference_in_json_list(acc_list, prd_list):
    list_differences = []

    for prd_value in prd_list:
        for acc_value in acc_list:
            if prd_value["id"] == acc_value["id"]:
                value_diff = DeepDiff(prd_value, acc_value, ignore_order=True)
                if value_diff != {}:
                    list_differences.append(value_diff.tree)

    return list_differences
