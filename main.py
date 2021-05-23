import os

import account_scan
import argparse

description = """Scan one account and obtain friends/followers information. 
Then that information is filtered by "judge_user_info" method, and 
summarized into markdown."""

def main():
    args = parse_args()

    if not os.path.exists("./profile_jpg"):
        os.mkdir("./profile_jpg")

    if not os.path.exists("./markdown"):
        os.mkdir("./markdown")

    ac_scan = account_scan.AccountUtils()
    ac_scan.set_api()

    ac_scan.markdown_target_accounts(args.screen_name, tp=args.type, open_=True)
    ac_scan.check_api_rate_limit(f"API.{args.type}_ids")

def parse_args():
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("screen_name", help="screen_name of target twitter account") 
    parser.add_argument("--type","-t",choices = ["friends","followers"], required=True,
        help="which type will be extracted, friends or followers.")
    args   = parser.parse_args()
    return(args)

if __name__ == "__main__":
    main()

