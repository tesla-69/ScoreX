import { useState, useEffect } from 'react';

const Dashboard = () => {
  const [candidates, setCandidates] = useState([]);
  const [selectedMatch, setSelectedMatch] = useState(1);
  const [matchData, setMatchData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCandidates();
  }, []);

  useEffect(() => {
    if (selectedMatch) {
      fetchMatchData(selectedMatch);
    }
  }, [selectedMatch]);

  const fetchCandidates = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/top-matches');
      const data = await response.json();
      if (data.status === "success") {
        setCandidates(data.candidates);
      } else {
        console.error('Error fetching candidates:', data.detail);
      }
    } catch (error) {
      console.error('Error fetching candidates:', error);
    }
  };

  const fetchMatchData = async (matchNumber) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/results/${matchNumber}`);
      const data = await response.json();
      if (data.status === "success") {
        setMatchData({
          ...data,
          graphUrl: `http://localhost:8000${data.graphUrl}`,
          wordcloudUrl: `http://localhost:8000${data.wordcloudUrl}`
        });
      } else {
        console.error('Error fetching match data:', data.detail);
      }
    } catch (error) {
      console.error('Error fetching match data:', error);
    }
    setLoading(false);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-6 text-gray-800">Resume Match Dashboard</h1>

      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {candidates.map((candidate, idx) => (
          <div
            key={idx}
            onClick={() => setSelectedMatch(idx + 1)}
            className={`cursor-pointer p-4 rounded-lg shadow-md transition-all duration-200 hover:shadow-xl ${
              selectedMatch === idx + 1 ? 'bg-blue-600 text-white' : 'bg-white text-gray-800'
            }`}
          >
            <h2 className="text-lg font-semibold">Match {idx + 1}</h2>
            <p className="text-sm mt-1">{candidate.name}</p>
            <p className="text-sm">Score: <span className="font-bold">{candidate.score}%</span></p>
          </div>
        ))}
      </div>

      {loading ? (
        <div className="text-center text-gray-600 text-lg">Loading results...</div>
      ) : matchData ? (
        <div className="space-y-8">
          {/* Charts Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Match Graph</h2>
              <img src={matchData.graphUrl} alt="Match Graph" className="w-full rounded-md" />
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Word Cloud</h2>
              <img src={matchData.wordcloudUrl} alt="Word Cloud" className="w-full rounded-md" />
            </div>
          </div>

          {/* Detailed Results Table */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Detailed Results</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto border border-gray-200">
                <thead>
                  <tr className="bg-gray-100 text-left text-sm">
                    <th className="px-4 py-2 border">Area</th>
                    <th className="px-4 py-2 border">Match %</th>
                    <th className="px-4 py-2 border">Matching Keywords</th>
                    <th className="px-4 py-2 border">Missing Keywords</th>
                  </tr>
                </thead>
                <tbody>
                  {matchData.results.map((result, index) => (
                    <tr key={index} className="border-t">
                      <td className="px-4 py-2 border">{result.Area}</td>
                      <td className="px-4 py-2 border">{result['Match %']}%</td>
                      <td className="px-4 py-2 border text-green-600">{result['Matching Keywords']}</td>
                      <td className="px-4 py-2 border text-red-600">{result['Missing Keywords']}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-600">No data available</div>
      )}
    </div>
  );
};

export default Dashboard;
