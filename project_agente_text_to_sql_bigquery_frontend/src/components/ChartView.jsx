import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'


const COLORS = [
  '#2563eb',
  '#16a34a',
  '#dc2626',
  '#9333ea',
  '#ea580c',
]


export default function ChartView({ spec }) {

  if (!spec?.data?.length) return null

  const {
    type,
    title,
    xKey,
    yKeys = [],
    data
  } = spec

  if (type === 'metric') {

    const valueKey = yKeys[0]

    return (
      <div className="chart-card chart-card--metric">
        <h3>{title}</h3>

        <div className="metric-value">
          {data[0]?.[valueKey]}
        </div>
      </div>
    )
  }


  if (type === 'bar') {

    return (
      <div className="chart-card">

        <h3>{title}</h3>

        <ResponsiveContainer width="100%" height={350}>

          <BarChart data={data}>

            <CartesianGrid strokeDasharray="3 3" />

            <XAxis
              dataKey={xKey}
              interval={0}
              angle={-20}
              textAnchor="end"
              height={80}
            />

            <YAxis />

            <Tooltip />

            <Legend />

            {yKeys.map((key, i) => (
              <Bar
                key={key}
                dataKey={key}
                fill={COLORS[i % COLORS.length]}
              />
            ))}

          </BarChart>

        </ResponsiveContainer>

      </div>
    )
  }


  if (type === 'line') {

    return (
      <div className="chart-card">

        <h3>{title}</h3>

        <ResponsiveContainer width="100%" height={350}>

          <LineChart data={data}>

            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey={xKey} />

            <YAxis />

            <Tooltip />

            <Legend />

            {yKeys.map((key, i) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={COLORS[i % COLORS.length]}
              />
            ))}

          </LineChart>

        </ResponsiveContainer>

      </div>
    )
  }


  if (type === 'pie') {

    return (
      <div className="chart-card">

        <h3>{title}</h3>

        <ResponsiveContainer width="100%" height={350}>

          <PieChart>

            <Tooltip />

            <Legend />

            <Pie
              data={data}
              dataKey={yKeys[0]}
              nameKey={xKey}
              label
            />

          </PieChart>

        </ResponsiveContainer>

      </div>
    )
  }


  if (type === 'scatter') {

    return (
      <div className="chart-card">

        <h3>{title}</h3>

        <ResponsiveContainer width="100%" height={350}>

          <ScatterChart>

            <CartesianGrid />

            <XAxis
              dataKey={xKey}
              name={xKey}
              type="number"
            />

            <YAxis
              dataKey={yKeys[0]}
              name={yKeys[0]}
              type="number"
            />

            <Tooltip />

            <Scatter data={data} />

          </ScatterChart>

        </ResponsiveContainer>

      </div>
    )
  }


  return null
}