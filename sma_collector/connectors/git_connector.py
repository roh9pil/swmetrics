
,<큰으러러려ㅕㄱ bi hi Jenni '/'.join(repo_url.split('/')[-2:]).replace('.git', '')

    def _clone_or_open_repo(self):
        try:
            repo = Repo(self.repo_path)
            logging.info(f"Repository found at {self.repo_path}, pulling latest changes.")
            repo.remotes.origin.pull()
        except (GitCommandError, NoSuchPathError, IndexError):
            logging.info(f"Repository not found or invalid, cloning from {self.repo_url}")
            repo = Repo.clone_from(self.repo_url, self.repo_path)
        return repo

    def collect_commits(self, max_count=1000) -> list[dict]:
        commits =
        for commit in self._repo.iter_commits('HEAD', max_count=max_count):
            commits.append({
                "sha": commit.hexsha,
                "author_name": commit.author.name,
                "author_email": commit.author.email,
                "authored_date": commit.authored_datetime,
                "message": commit.message.strip(),
            })
        logging.info(f"Collected {len(commits)} commits.")
        return commits

    def collect_pull_requests(self, max_count=100) -> list[dict]:
        reviews =
        if not self.github_client:
            logging.warning("GitHub token not provided. Skipping PR collection.")
            return reviews
        try:
            repo = self.github_client.get_repo(self.github_repo_name)
            pulls = repo.get_pulls(state='all', sort='created', direction='desc')
            
            for pr in pulls[:max_count]:
                first_comment_date = None
                comments = pr.get_issue_comments()
                if comments.totalCount > 0:
                    # get_issue_comments() is a PaginatedList, need to get the first element
                    first_comment_date = comments.created_at

                time_to_first_review = None
                if first_comment_date:
                    time_to_first_review = (first_comment_date - pr.created_at).total_seconds() / 60

                time_to_merge = None
                if pr.merged_at:
                    time_to_merge = (pr.merged_at - pr.created_at).total_seconds() / 60

                reviews.append({
                    "id": f"{repo.id}-{pr.number}",
                    "repo_name": self.github_repo_name,
                    "pr_number": pr.number,
                    "title": pr.title,
                    "author": pr.user.login,
                    "created_date": pr.created_at,
                    "merged_date": pr.merged_at,
                    "first_comment_date": first_comment_date,
                    "time_to_first_review_minutes": int(time_to_first_review) if time_to_first_review else None,
                    "time_to_merge_minutes": int(time_to_merge) if time_to_merge else None,
                    "comment_count": pr.comments,
                })
            logging.info(f"Collected {len(reviews)} pull requests from GitHub.")
        except Exception as e:
            logging.error(f"Failed to collect GitHub pull requests: {e}")
        return reviews

