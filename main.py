import sys
import threading
import time
import src.db as db
import src.crawler as crawler
import src.searcher as searcher

def print_help():
    print("\n--- Multi-Agent Web Crawler CLI ---")
    print("Commands:")
    print("  index <url> <depth>   : Start crawling from <url> up to <depth> hops.")
    print("  search <query>        : Search the indexed pages for <query>.")
    print("  resume                : Refresh any stalled jobs back to pending.")
    print("  status                : Display crawler progress and detailed metrics.")
    print("  help                  : Show this message.")
    print("  exit / quit           : Stop crawler and exit application.")

def main():
    print("Initializing Multi-Agent Database (Architect Agent)...")
    db.init_db()
    
    print("Starting Crawler Daemons (Crawler Agent)...")
    crawler.start_crawling()
    
    print_help()
    
    try:
        while True:
            cmd_input = input("\n> ").strip().split()
            if not cmd_input:
                continue
                
            command = cmd_input[0].lower()
            
            if command in ('exit', 'quit'):
                print("Stopping threads and exiting...")
                crawler.stop_crawling()
                break
            
            elif command == 'help':
                print_help()
                
            elif command == 'status':
                pending = db.get_queue_depth()
                crawled = db.get_crawled_count()
                active = db.get_active_count()
                failed = db.get_failed_count()
                max_depth = db.get_max_seen_depth()
                print(f"[STATUS] Crawled: {crawled} | Active: {active} | Failed: {failed}")
                print(f"         Pending Queue: {pending} (Back-pressure threshold: {crawler.MAX_QUEUE_DEPTH})")
                print(f"         Max Depth Seen: {max_depth}")
            
            elif command == 'resume':
                print("[RESUME] Forcing all processing/stalled jobs back to pending.")
                db.force_resume_all()
                print("[RESUME] Resume complete.")
            
            elif command == 'index':
                if len(cmd_input) < 3:
                    print("Usage: index <url> <depth>")
                    continue
                url = cmd_input[1]
                try:
                    k = int(cmd_input[2])
                    added = crawler.index(url, k)
                    if added:
                        print(f"[INDEX] Added {url} to crawl queue with max_depth {k}.")
                    else:
                        print(f"[INDEX] Ignored: {url} is already in the queue or has been crawled before.")
                except ValueError:
                    print("Depth must be an integer.")
            
            elif command == 'search':
                if len(cmd_input) < 2:
                    print("Usage: search <query>")
                    continue
                query = " ".join(cmd_input[1:])
                print(f"[SEARCH] Searching for: '{query}'...")
                
                start_t = time.time()
                results = searcher.search(query)
                elapsed = time.time() - start_t
                
                print(f"[SEARCH] Found {len(results)} results in {elapsed:.4f}s.")
                for i, (rel_url, orig_url, depth) in enumerate(results[:10]):
                    print(f"  {i+1}. URL: {rel_url}")
                    print(f"     Origin: {orig_url} | Discovered at Depth: {depth}")
                
                if len(results) > 10:
                    print(f"  ... and {len(results) - 10} more.")
            else:
                print(f"Unknown command: {command}")
                
    except KeyboardInterrupt:
        print("\nForce stopping...")
        crawler.stop_crawling()
        sys.exit(0)

if __name__ == "__main__":
    main()
