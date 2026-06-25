import type {
  ActionItem,
  GlobalSearchResponse,
  MeetingDetail,
  MeetingListItem,
  MeetingUpdatePayload,
  TranscriptSearchResponse,
} from "./types";

const API_BASE_URL =
process.env.NEXT_PUBLIC_API_URL ??
"https://fireflies-ai-clone-dtxd.onrender.com";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const message = errorBody?.error?.message ?? response.statusText;
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function getMeetings(
  params: URLSearchParams,
): Promise<MeetingListItem[]> {
  const queryString = params.toString();
  return request(`/meetings${queryString ? `?${queryString}` : ""}`);
}

export function getTags(): Promise<{ id: number; name: string }[]> {
  return request(`/tags`);
}

export function createTag(name: string): Promise<{ id: number; name: string }> {
  return request(`/tags?name=${encodeURIComponent(name)}`, { method: "POST" });
}

export function getMeeting(id: number): Promise<MeetingDetail> {
  return request(`/meetings/${id}`);
}

export function getTranscript(
  id: number,
  search?: string,
): Promise<TranscriptSearchResponse> {
  const params = new URLSearchParams();
  if (search?.trim()) {
    params.set("search", search.trim());
  }
  const queryString = params.toString();
  return request(
    `/meetings/${id}/transcript${queryString ? `?${queryString}` : ""}`,
  );
}

export function updateMeeting(
  id: number,
  payload: MeetingUpdatePayload,
): Promise<MeetingDetail> {
  return request(`/meetings/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function createActionItem(
  meetingId: number,
  payload: { text: string; assignee?: string | null; due_date?: string | null },
): Promise<ActionItem> {
  return request(`/meetings/${meetingId}/action-items`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function updateActionItem(
  actionItemId: number,
  payload: Partial<ActionItem>,
): Promise<ActionItem> {
  return request(`/action-items/${actionItemId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function deleteActionItem(
  actionItemId: number,
): Promise<{ message: string }> {
  return request(`/action-items/${actionItemId}`, { method: "DELETE" });
}

export function generateSummary(meetingId: number): Promise<MeetingDetail> {
  return request(`/meetings/${meetingId}/generate-summary`, { method: "POST" });
}

export function searchWorkspace(query: string): Promise<GlobalSearchResponse> {
  const params = new URLSearchParams({ q: query });
  return request(`/search?${params.toString()}`);
}

export function askQuestion(
  meetingId: number | null,
  question: string,
): Promise<{ answer: string; source?: string | null }> {
  return request(`/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ meeting_id: meetingId, question }),
  });
}

export async function createMeeting(
  formData: FormData,
): Promise<MeetingDetail> {
  const response = await fetch(`${API_BASE_URL}/meetings`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const message = errorBody?.error?.message ?? response.statusText;
    throw new Error(message);
  }

  return response.json() as Promise<MeetingDetail>;
}
