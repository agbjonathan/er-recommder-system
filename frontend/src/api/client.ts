import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

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
  user_location: {
    latitude: number;
    longitude: number;
  };
}

export interface CongestionFeature {
  type: "Feature";
  geometry: {
    type: "Point";
    coordinates: [number, number];
  };
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
  type: "FeatureCollection";
  features: CongestionFeature[];
  generated_at: string;
}

export const getRecommendations = (lat: number, lng: number, maxDistance = 10) =>
  api.get<RecommendationResponse>('/recommend', {
    params: { latitude: lat, longitude: lng, max_distance: maxDistance },
  });

export const getCongestionMap = () =>
  api.get<CongestionMapResponse>('/dashboard/congestion/map');

export default api;
