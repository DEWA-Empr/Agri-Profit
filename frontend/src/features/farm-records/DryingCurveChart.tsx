import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { colors } from '../../styles/theme';
import type { DryingParams } from '../../types/domain';

// The drying curve: measured moisture against time for one run.
//
// EVERY POINT IS MEASURED. The series is the run's own start
// (t=0, moisture_initial_wb), the intermediate readings the farmer entered, and
// its end (t=drying_time_hours, moisture_final_wb) — all four values come
// straight off GET /bioprocess/{id}. Nothing here is fitted, smoothed,
// extrapolated or recomputed.
//
// The fitted Newton and Page models are DELIBERATELY NOT DRAWN, even though
// `metrics.newton_k` and `metrics.page` are returned and would plot. Drawing
// them would mean implementing the kinetics a second time in the browser, and
// this project has already been bitten by exactly that: the partial budget was
// implemented twice and nothing compared the two until a shared fixture was
// added (docs/EVIDENCE.md). Their parameters are reported as numbers beside the
// chart instead, where the backend's own arithmetic is the only source.
//
// A curve is also a record here, not a forecast — which is why the "not a
// chart" reasoning on SensitivityTable does not apply. That table would have
// projected prices at yields nobody harvested; this plots readings somebody took.

export const DryingCurveChart = ({ params }: { params: DryingParams }) => {
  const readings = params.readings ?? [];

  const data = [
    { time_hours: 0, moisture_wb: params.moisture_initial_wb },
    ...readings.map((r) => ({ time_hours: r.time_hours, moisture_wb: r.moisture_wb })),
    { time_hours: params.drying_time_hours, moisture_wb: params.moisture_final_wb },
  ];

  return (
    <div style={{ width: '100%', height: 190 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 6, right: 12, bottom: 4, left: -14 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={colors.dividerLight} vertical={false} />
          <XAxis
            dataKey="time_hours"
            type="number"
            domain={[0, params.drying_time_hours]}
            tick={{ fontSize: 10, fill: colors.textMuted }}
            tickLine={false}
            axisLine={{ stroke: colors.border }}
            label={{ value: 'Hours', position: 'insideBottomRight', offset: -2, fontSize: 10, fill: colors.textMuted }}
          />
          <YAxis
            tick={{ fontSize: 10, fill: colors.textMuted }}
            tickLine={false}
            axisLine={{ stroke: colors.border }}
            width={44}
            label={{ value: '% wb', angle: -90, position: 'insideLeft', offset: 16, fontSize: 10, fill: colors.textMuted }}
          />
          <Tooltip
            // recharts types these as ValueType / ReactNode, so the formatters
            // take the widened type and narrow here rather than lying about it.
            formatter={(value) => [`${String(value)}% wet basis`, 'Moisture'] as [string, string]}
            labelFormatter={(hours) => `${String(hours)} h`}
            contentStyle={{ fontSize: '11px', borderRadius: '8px', border: `0.5px solid ${colors.border}` }}
          />
          <Line
            type="monotone"
            dataKey="moisture_wb"
            stroke={colors.primary}
            strokeWidth={2}
            // Dots on every point, because each one is a measurement the farmer
            // took and the count is the thing that decides whether a Page fit
            // exists at all.
            dot={{ r: 3, fill: colors.primary, strokeWidth: 0 }}
            activeDot={{ r: 5 }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
