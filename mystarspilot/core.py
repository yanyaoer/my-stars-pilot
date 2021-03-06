# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from colorama import Fore, Back, Style
from getpass import getpass, getuser
from github3 import login
from .db import StarredDB
from .view import SearchResultView
from . import __version__
import argparse
import os
import sys
try:
    import readline
except ImportError:
    import pyreadline as readline
    
STAR_PILOT_HOME = os.path.join(os.path.expanduser("~"), ".mystarspilot")


def main():
    
    if not os.path.exists(STAR_PILOT_HOME):
        os.makedirs(STAR_PILOT_HOME)
    
    parser = argparse.ArgumentParser(
        description="a CLI tool to search your starred Github repositories.")
    parser.add_argument("keywords", nargs='*', help="search keywords")
    parser.add_argument("-l", "--language", 
        help="filter by language", nargs='+')
    parser.add_argument("-u", "--update", action="store_true", 
        help="create(first time) or update the local stars index")
    parser.add_argument("-r", "--reindex", action="store_true", 
        help="re-create the local stars index")
    parser.add_argument("-a", "--alfred", action="store_true", 
        help="format search result as Alfred XML")
    parser.add_argument('-v', '--version', action='version', 
        version='%(prog)s ' + __version__)
    
    args = parser.parse_args()
    
    if args.update or args.reindex:
        
        try:
            user = raw_input('GitHub username: ')
        except KeyboardInterrupt:
            user = getuser()
        else:
            if not user:
                user = getuser()
            
        password = getpass('GitHub password for {0}: '.format(user))
        
        if not password:
            print(Fore.RED + "password is required.")
            sys.exit(1)
            
        g = login(user, password)
        
        mode = 't' if args.reindex else 'w'
        
        with StarredDB(STAR_PILOT_HOME, mode) as db:
            repo_list = []
            
            for repo in g.iter_starred():
                if db.get_latest_repo_full_name() == repo.full_name:
                    break
                print(Fore.BLUE + repo.full_name + Fore.RESET)
                repo_list.append({
                    'full_name': repo.full_name,
                    'name': repo.name,
                    'url': repo.html_url,
                    'language': repo.language,
                    'description': repo.description,
                })
            if repo_list:
                print(Fore.GREEN + 'Saving repo data...')
                db.update(repo_list)
                print(Fore.RED + 'Done.' + Fore.RESET)   
            else:
                print(Fore.RED + 'No new stars found.' + Fore.RESET)
            
             
        sys.exit(0)
       
    if not args.keywords and not args.language:
        parser.print_help()
        sys.exit(0)
    
    with StarredDB(STAR_PILOT_HOME, mode='r') as db:
        search_result = db.search(args.language, args.keywords)
    
    SearchResultView().print_search_result(
        search_result, args.keywords, alfred_format=args.alfred)
