export interface Repository {
  tiktok_url: string;
  tiktok_author: string;
  github_url: string;
  repo_full_name: string;
  repo_name: string;
  owner: string;
  star_count: number;
  fork_count: number;
  description: string | null;
  primary_language: string | null;
  topics: string[];
  homepage: string | null;
  ai_summary: string;
  frames: string[];
}

export interface AnalyzeResponse {
  success: boolean;
  repository?: Repository;
  error?: string;
}
