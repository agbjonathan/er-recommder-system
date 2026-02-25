import { useState } from 'react';
import { getRecommendations, Hospital } from '../api/client';

export default function Home() {
  const [results, setResults] = useState<Hospital[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLocate = () => {
    if (!navigator.geolocation) {
      setError('Geolocation not supported');
      return;
    }

    setLoading(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const res = await getRecommendations(
            position.coords.latitude,
            position.coords.longitude
          );
          setResults(res.data.results);
        } catch {
          setError('Failed to fetch recommendations');
        } finally {
          setLoading(false);
        }
      },
      () => {
        setError('Unable to get your location');
        setLoading(false);
      }
    );
  };

  const getRiskColor = (risk: string | null) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center py-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-4">
          Find the Best ER Near You
        </h2>
        <p className="text-gray-600 mb-6">
          Get recommendations based on distance and predicted wait times
        </p>
        <button
          onClick={handleLocate}
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold 
                     hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {loading ? 'Finding...' : '📍 Use My Location'}
        </button>
        {error && <p className="text-red-500 mt-4">{error}</p>}
      </div>

      {results.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {results.map((hospital) => (
            <div
              key={hospital.hospital_id}
              className="bg-white rounded-lg shadow p-4 border border-gray-200"
            >
              <h3 className="font-semibold text-lg text-gray-800">
                {hospital.name}
              </h3>
              <p className="text-gray-600 text-sm mt-1">
                {hospital.distance_km.toFixed(1)} km away
              </p>
              <div className="mt-3 flex items-center justify-between">
                <span className={`px-2 py-1 rounded text-sm font-medium ${getRiskColor(hospital.risk_level)}`}>
                  {hospital.risk_level ?? 'Unknown'} risk
                </span>
                {hospital.predicted_pressure && (
                  <span className="text-gray-500 text-sm">
                    Pressure: {hospital.predicted_pressure.toFixed(1)}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
