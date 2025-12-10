export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();

  try {
    if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });
    const owner = process.env.GITHUB_OWNER;
    const repo = process.env.GITHUB_REPO;
    const branch = process.env.GITHUB_BRANCH || 'main';
    if (!owner || !repo) return res.status(500).json({ error: 'Server not configured' });

    const date = req.query.date;
    if (!date) return res.status(400).json({ error: 'Missing date' });

    const path = `data/schedules/${date}.json`;
    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${encodeURIComponent(path)}?ref=${encodeURIComponent(branch)}`;
    const token = process.env.GITHUB_TOKEN;
    const headers = { Accept: 'application/vnd.github.v3+json' };
    if (token) headers.Authorization = `token ${token}`;

    const r = await fetch(apiUrl, { headers });
    if (r.status === 404) return res.status(404).json({ error: 'Not found' });
    if (!r.ok) {
      const txt = await r.text();
      return res.status(500).json({ error: 'GitHub API error: ' + txt });
    }
    const data = await r.json();
    const decoded = Buffer.from(data.content.replace(/\n/g, ''), 'base64').toString('utf8');
    // parse JSON
    const payload = JSON.parse(decoded);
    return res.status(200).json({ date, payload });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: String(err) });
  }
}
