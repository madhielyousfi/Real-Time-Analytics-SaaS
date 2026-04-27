'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';

interface ChartProps {
  data: Array<{ timestamp: string; value: number }>;
  dataKey?: string;
  color?: string;
}

export const LineChartComponent = ({ data, dataKey = 'value', color = '#8884d8' }: ChartProps) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis
          dataKey="timestamp"
          tickFormatter={(str) => format(parseISO(str), 'MMM d, HH:mm')}
          stroke="#666"
        />
        <YAxis stroke="#666" />
        <Tooltip
          labelFormatter={(str) => format(parseISO(str), 'MMM d, HH:mm')}
          formatter={(value: number) => [value.toFixed(2), 'Count']}
        />
        <Line
          type="monotone"
          dataKey={dataKey}
          stroke={color}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};