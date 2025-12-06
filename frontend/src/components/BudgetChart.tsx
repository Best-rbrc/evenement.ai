import { BudgetItem } from '@/types/event';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface BudgetChartProps {
  breakdown: BudgetItem[];
  total: number;
}

const COLORS = [
  'hsl(15, 75%, 55%)',   // soft-coral
  'hsl(175, 50%, 40%)',  // accent/teal
  'hsl(40, 90%, 50%)',   // gold
  'hsl(15, 60%, 75%)',   // rose-gold
  'hsl(140, 25%, 75%)',  // sage
  'hsl(30, 15%, 50%)',   // muted
];

export function BudgetChart({ breakdown, total }: BudgetChartProps) {
  const data = breakdown.map((item) => ({
    name: item.category,
    value: item.amount,
    percentage: item.percentage,
  }));

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="w-full">
      <div className="text-center mb-4">
        <p className="text-sm text-muted-foreground">Total Budget</p>
        <p className="text-3xl font-display font-bold text-primary">{formatCurrency(total)}</p>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => formatCurrency(value)}
            contentStyle={{
              backgroundColor: 'hsl(var(--card))',
              border: '1px solid hsl(var(--border))',
              borderRadius: '12px',
              boxShadow: 'var(--shadow-medium)',
            }}
          />
          <Legend
            formatter={(value: string) => (
              <span className="text-sm text-foreground">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 space-y-2">
        {breakdown.map((item, i) => (
          <div key={i} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: COLORS[i % COLORS.length] }}
              />
              <span>{item.category}</span>
            </div>
            <span className="font-medium">{formatCurrency(item.amount)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
