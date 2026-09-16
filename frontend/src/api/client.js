const API_BASE = '/api';

export async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}`;
    try {
      const errData = await response.json();
      if (errData.detail) {
        errorMsg = errData.detail;
      }
    } catch (e) {
      // JSON parse fallback
    }
    throw new Error(errorMsg);
  }

  return response.json();
}

export const api = {
  ingest: (query, max_results = 10) =>
    apiFetch('/ingest', {
      method: 'POST',
      body: JSON.stringify({ query, max_results }),
    }),

  listAbstracts: (limit = 20) =>
    apiFetch(`/abstracts?limit=${limit}`),

  getAbstractDetail: (abstractId) =>
    apiFetch(`/abstracts/${abstractId}`),

  search: (params = {}) => {
    const queryStr = new URLSearchParams(params).toString();
    return apiFetch(`/search?${queryStr}`);
  },

  exportUrl: (params = {}, format = 'csv') => {
    const queryParams = new URLSearchParams({ ...params, format });
    return `${API_BASE}/export?${queryParams.toString()}`;
  },

  submitReview: (target_table, target_id, status, corrected_value = null) =>
    apiFetch('/review', {
      method: 'POST',
      body: JSON.stringify({
        target_table,
        target_id,
        status,
        corrected_value,
        reviewed_by: 'human_reviewer',
      }),
    }),

  getReviewQueue: (limit = 50) =>
    apiFetch(`/review/queue?limit=${limit}`),

  bulkApprove: (minConfidence = 0.85) =>
    apiFetch(`/review/bulk-approve?min_confidence=${minConfidence}`, {
      method: 'POST',
    }),

  getEvaluationLatest: () =>
    apiFetch('/evaluation/latest'),

  runEvaluation: (task = 'ALL', dataset_version = 'v1.0-gold') =>
    apiFetch(`/evaluation/run?task=${task}&dataset_version=${dataset_version}`, {
      method: 'POST',
    }),
};
