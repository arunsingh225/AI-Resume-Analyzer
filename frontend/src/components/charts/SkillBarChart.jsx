import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts'

export default function SkillBarChart({ found = [], missing = [], advanced = [] }) {
  const data = [
    { name: 'Core Found',     count: found.length,    color: '#4E7245' },
    { name: 'Core Missing',   count: missing.length,  color: '#9B3A3A' },
    { name: 'Advanced Found', count: advanced.length,  color: '#4B5570' },
  ].filter(d => d.count > 0)

  if (data.length === 0) return null

  return (
    <div className="w-full h-[180px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20, top: 5, bottom: 5 }}>
          <XAxis
            type="number"
            tick={{ fontSize: 11, fill: '#78716C' }}
            axisLine={{ stroke: '#E7E5E4' }}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 11, fill: '#57534E', fontFamily: 'DM Sans' }}
            width={110}
            axisLine={false}
            tickLine={false}
          />
          <Bar dataKey="count" radius={[0, 6, 6, 0]} barSize={22}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
          <Tooltip
            contentStyle={{
              borderRadius: 12,
              border: '1px solid #E3E1DF',
              fontSize: 12,
              background: 'rgba(255,255,255,0.95)',
            }}
            formatter={(value) => [value, 'Skills']}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
