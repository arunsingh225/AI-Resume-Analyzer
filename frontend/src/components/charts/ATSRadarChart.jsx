import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Tooltip } from 'recharts'

export default function ATSRadarChart({ ats }) {
  if (!ats) return null

  const data = [
    { subject: 'Keywords',   score: ats.keyword_score || 0,    fullMark: 100 },
    { subject: 'Formatting', score: ats.formatting_score || 0, fullMark: 100 },
    { subject: 'Sections',   score: ats.section_score || 0,    fullMark: 100 },
    { subject: 'Experience', score: ats.experience_score || 0, fullMark: 100 },
    { subject: 'Skills',     score: ats.skill_score || 0,      fullMark: 100 },
  ]

  return (
    <div className="w-full h-[280px]">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="#E7E5E4" strokeDasharray="3 3" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fontSize: 11, fill: '#78716C', fontFamily: 'DM Sans' }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fontSize: 9, fill: '#A8A29E' }}
            axisLine={false}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke="#4E7245"
            fill="#4E7245"
            fillOpacity={0.15}
            strokeWidth={2}
            dot={{ r: 3, fill: '#4E7245' }}
          />
          <Tooltip
            contentStyle={{
              borderRadius: 12,
              border: '1px solid #E3E1DF',
              fontSize: 12,
              fontFamily: 'DM Sans',
              background: 'rgba(255,255,255,0.95)',
              backdropFilter: 'blur(8px)',
              boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
            }}
            formatter={(value) => [`${value}/100`, 'Score']}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
