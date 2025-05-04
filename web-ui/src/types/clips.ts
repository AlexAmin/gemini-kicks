export interface Clip {
  id: string;
  type: "video" | "audio";
  duration: number;
  url: string;
  timestamp: string;
  status: "processing" | "completed" | "failed";
}

export interface GenerationStatus {
  totalClips: number;
  completedClips: number;
  audioSummaryStatus: "not_started" | "processing" | "completed" | "failed";
}