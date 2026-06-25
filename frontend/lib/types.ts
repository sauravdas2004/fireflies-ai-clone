export type Participant = {
  id: number;
  meeting_id?: number;
  name: string;
  email?: string | null;
  role?: string | null;
};

export type Tag = {
  id: number;
  name: string;
};

export type Summary = {
  id: number;
  meeting_id?: number;
  overview_text: string;
  generated_at: string;
};

export type KeyTopic = {
  id: number;
  meeting_id?: number;
  topic_text: string;
  order_index: number;
};

export type ActionItem = {
  id: number;
  meeting_id?: number;
  text: string;
  assignee?: string | null;
  is_completed: boolean;
  due_date?: string | null;
  created_at?: string;
};

export type TranscriptMatchRange = {
  start: number;
  end: number;
};

export type TranscriptSegment = {
  id: number;
  meeting_id: number;
  speaker_name: string;
  start_time: number;
  end_time: number;
  text: string;
  order_index: number;
  match_ranges?: TranscriptMatchRange[];
};

export type User = {
  id: number;
  name: string;
  email: string;
  avatar_url?: string | null;
};

export type MeetingListItem = {
  id: number;
  title: string;
  date: string;
  duration_seconds: number;
  audio_url?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  created_by_user?: User;
  participants: Participant[];
  tags: Tag[];
};

export type MeetingDetail = MeetingListItem & {
  summary?: Summary | null;
  transcript_segments: TranscriptSegment[];
  key_topics: KeyTopic[];
  action_items: ActionItem[];
};

export type GlobalSearchResult = {
  meeting_id: number;
  title: string;
  date: string;
  snippet: string;
  match_count: number;
  participants: Participant[];
  tags: Tag[];
};

export type GlobalSearchResponse = {
  query: string;
  results: GlobalSearchResult[];
};

export type TranscriptSearchResponse = {
  meeting_id: number;
  query?: string | null;
  segments: TranscriptSegment[];
};

export type MeetingUpdatePayload = {
  title?: string | null;
  participants?:
    | {
        name: string;
        email?: string | null;
        role?: string | null;
      }[]
    | null;
};
