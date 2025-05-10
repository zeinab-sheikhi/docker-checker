import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class RingChartWidget extends StatelessWidget {
  final Map<String, int> severityCounts;

  const RingChartWidget({super.key, required this.severityCounts});

  @override
  Widget build(BuildContext context) {
    final total = severityCounts.values.fold<int>(0, (a, b) => a + b);
    final colors = {
      'Critical': Colors.redAccent,
      'High': Colors.orange,
      'Medium': Colors.amber,
      'Low': Colors.blue,
    };
    final sections = severityCounts.entries.map((entry) {
      final color = colors[entry.key] ?? Colors.grey;
      final value = entry.value.toDouble();
      return PieChartSectionData(
        color: color,
        value: value,
        title: entry.value > 0 ? entry.value.toString() : '',
        radius: 40,
        titleStyle: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
      );
    }).toList();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          height: 180,
          width: 180,
          child: PieChart(
            PieChartData(
              sections: sections,
              centerSpaceRadius: 50,
              sectionsSpace: 2,
              startDegreeOffset: -90,
              borderData: FlBorderData(show: false),
              pieTouchData: PieTouchData(enabled: false),
            ),
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 16,
          children: severityCounts.keys.map((key) {
            final color = colors[key] ?? Colors.grey;
            return Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(width: 12, height: 12, color: color),
                const SizedBox(width: 4),
                Text('$key: ${severityCounts[key]}'),
              ],
            );
          }).toList(),
        ),
      ],
    );
  }
} 