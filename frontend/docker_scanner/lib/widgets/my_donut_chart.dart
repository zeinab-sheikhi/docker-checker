import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import '../consts.dart';

class MyDonutChart extends StatefulWidget {
  final Map<String, int> severityCounts;

  const MyDonutChart({super.key, required this.severityCounts});

  @override
  State<MyDonutChart> createState() => _MyDonutChartState();
}

class _MyDonutChartState extends State<MyDonutChart> {
  int? touchedIndex;

  @override
  Widget build(BuildContext context) {
    final total = widget.severityCounts.values.fold<int>(0, (a, b) => a + b);
    final colors = {
      'critical': kCriticalSeverity,
      'high': kHighSeverity,
      'medium': kMediumSeverity,
      'low': kLowSeverity,
    };

    final keys = widget.severityCounts.keys.toList();

    List<PieChartSectionData> sections = [];
    for (int i = 0; i < keys.length; i++) {
      final key = keys[i];
      final value = widget.severityCounts[key]!;
      final isTouched = i == touchedIndex;
      sections.add(
        PieChartSectionData(
          color: colors[key.toLowerCase()] ?? grey,
          value: value.toDouble(),
          title: '$value',
          radius: isTouched ? 60 : 50,
          titleStyle: const TextStyle(
            color: white,
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
      );
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        SizedBox(
          height: 240,
          width: 240,
          child: PieChart(
            PieChartData(
              sections: sections,
              centerSpaceRadius: 70,
              sectionsSpace: 2,
              startDegreeOffset: -90,
              borderData: FlBorderData(show: false),
              pieTouchData: PieTouchData(
                enabled: true,
                touchCallback: (event, response) {
                  setState(() {
                    if (!event.isInterestedForInteractions ||
                        response == null ||
                        response.touchedSection == null) {
                      touchedIndex = null;
                      return;
                    }
                    touchedIndex = response.touchedSection!.touchedSectionIndex;
                  });
                },
              ),
            ),
            duration: const Duration(milliseconds: 350),
            curve: Curves.easeOut,
          ),
        ),
        const SizedBox(width: 32),
        // Legend
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children:
              keys.map((key) {
                final color = colors[key.toLowerCase()] ?? grey;
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(width: 18, height: 18, color: color),
                      const SizedBox(width: 8),
                      Text(
                        key,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
        ),
      ],
    );
  }
}
