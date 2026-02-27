import axios from 'axios';

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL ?? '/api' });

export interface Hospital {
  hospital_id: number;
  name: string;
  hospital_latitude: number;
  hospital_longitude: number;
  distance_km: number;
  predicted_pressure: number | null;
  risk_level: string | null;
  forecast_time: string | null;
}

export interface RecommendationResponse {
  results: Hospital[];
  user_location: { latitude: number; longitude: number };
}

export interface CongestionFeature {
  type: 'Feature';
  geometry: { type: 'Point'; coordinates: [number, number] };
  properties: {
    hospital_id: number;
    name: string;
    region: string;
    current_pressure: number | null;
    predicted_pressure: number | null;
    risk_level: string | null;
  };
}

export interface CongestionMapResponse {
  type: 'FeatureCollection';
  features: CongestionFeature[];
  generated_at: string;
}

export interface FeedbackPayload {
  category: 'ui' | 'accuracy' | 'suggestion';
  message: string | null;
}

export interface FeedbackResponse {
  id: number;
  category: string;
  message: string | null;
  created_at: string;
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

/** One point in the global 24-hour time series */
export interface PressureSeriesPoint {
  label: string;           // e.g. "14:00"
  predicted: number;
  observed: number | null; // null if not yet evaluated
}

/** Aggregate count of predicted vs observed forecasts per risk level */
export interface RiskComparisonItem {
  risk: 'LOW' | 'MEDIUM' | 'HIGH';
  predicted: number;
  observed: number;
}

/** Per-hospital summary row */
export interface HospitalPressureStat {
  hospital_id: number;
  name: string;
  mean_predicted: number;
  mean_observed: number | null;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
}

/** Response from GET /api/dashboard/stats */
export interface DashboardStatsResponse {
  global_series: PressureSeriesPoint[];
  risk_comparison: RiskComparisonItem[];
  hospital_stats: HospitalPressureStat[];
  generated_at: string;
}

// ─── API calls ────────────────────────────────────────────────────────────────

export const getRecommendations = (lat: number, lng: number, maxDistance = 10) =>
  api.get<RecommendationResponse>('/recommend', {
    params: { latitude: lat, longitude: lng, max_distance: maxDistance },
  });

export const getCongestionMap = (horizonHours: 1 | 2 | 4 =1) =>
  api.get<CongestionMapResponse>('/dashboard/congestion/map', {
    params: { horizon_hours: horizonHours },
  });

/**
 * New endpoint — see backend section in Docs for implementation.
 * GET /api/dashboard/stats?horizon_hours=1
 */
export const getDashboardStats = (horizonHours: 1 | 2 | 4 = 1, hospitalId?: number) =>
  api.get<DashboardStatsResponse>('/dashboard/stats', {
    params: { horizon_hours: horizonHours, ...(hospitalId ? { hospital_id: hospitalId } : {}) },
  });

export const submitFeedback = (payload: FeedbackPayload) =>
  api.post<FeedbackResponse>('/feedback', payload);

export default api;