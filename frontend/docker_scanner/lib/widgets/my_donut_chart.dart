import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import '../consts.dart';

class MyDonutChart extends StatelessWidget {
  final Map<String, int> severityCounts;
  final double width;
  final double height;

  const MyDonutChart({
    super.key,
    required this.severityCounts,
    this.width = 240,
    this.height = 240,
  });

  @override
  Widget build(BuildContext context) {
    final colors = {
      'critical': kCriticalSeverity,
      'high': kHighSeverity,
      'medium': kMediumSeverity,
      'low': kLowSeverity,
    };

    final keys = severityCounts.keys.toList();

    List<PieChartSectionData> sections =
        keys.map((key) {
          final value = severityCounts[key]!;
          return PieChartSectionData(
            color: colors[key.toLowerCase()] ?? grey,
            value: value.toDouble(),
            title: '$value',
            radius: 40,
            showTitle: true,
            titleStyle: const TextStyle(
              color: white,
              fontWeight: FontWeight.bold,
              fontSize: 20,
            ),
          );
        }).toList();

    return Container(
      // color: Colors.grey,
      height: height,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            flex: 7,
            child: PieChart(
              PieChartData(
                sections: sections,
                centerSpaceRadius: 70,
                sectionsSpace: 2,
                startDegreeOffset: -90,
                borderData: FlBorderData(show: false),
                pieTouchData: PieTouchData(enabled: false),
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children:
                  keys.map((key) {
                    final color = colors[key.toLowerCase()] ?? grey;
                    return Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 0,
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            width: 12,
                            height: 12,
                            decoration: BoxDecoration(
                              color: color,
                              borderRadius: BorderRadius.circular(2),
                            ),
                          ),
                          const SizedBox(width: 4),
                          Text(
                            key,
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}
