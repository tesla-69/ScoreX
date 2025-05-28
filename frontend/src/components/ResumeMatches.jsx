import { useState, useEffect } from 'react';

const ResumeMatches = () => {
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
      <h1 className="text-3xl font-bold mb-8">Resume Match Results</h1>
      
      <div className="flex space-x-4 mb-6">
        {[1, 2, 3].map((num) => (
          <button
            key={num}
            onClick={() => setSelectedMatch(num)}
            className={`px-4 py-2 rounded ${
              selectedMatch === num
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Match {num}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center">Loading...</div>
      ) : matchData ? (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Match Graph</h2>
              <img
                src={matchData.graphUrl}
                alt="Match Graph"
                className="w-full"
              />
            </div>
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Word Cloud</h2>
              <img
                src={matchData.wordcloudUrl}
                alt="Word Cloud"
                className="w-full"
              />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Detailed Results</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="px-4 py-2">Area</th>
                    <th className="px-4 py-2">Match %</th>
                    <th className="px-4 py-2">Matching Keywords</th>
                    <th className="px-4 py-2">Missing Keywords</th>
                  </tr>
                </thead>
                <tbody>
                  {matchData.results.map((result, index) => (
                    <tr key={index} className="border-b">
                      <td className="px-4 py-2">{result.Area}</td>
                      <td className="px-4 py-2">{result['Match %']}%</td>
                      <td className="px-4 py-2">{result['Matching Keywords']}</td>
                      <td className="px-4 py-2">{result['Missing Keywords']}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center">No data available</div>
      )}
    </div>
  );
};

export default ResumeMatches; 