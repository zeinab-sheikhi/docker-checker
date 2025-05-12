import 'package:flutter/material.dart';
import '../consts.dart';

class VulnerabilityRow {
  final String library;
  final String vulnerability;
  final String severity;
  final String fixedVersion;
  final String title;

  VulnerabilityRow({
    required this.library,
    required this.vulnerability,
    required this.severity,
    required this.fixedVersion,
    required this.title,
  });
}

class MyVulnerabilityTable extends StatelessWidget {
  final List<VulnerabilityRow> rows;

  const MyVulnerabilityTable({super.key, required this.rows});

  TextStyle get _titleStyle => const TextStyle(
    fontWeight: FontWeight.bold,
    color: kTextColor,
    fontSize: 15,
  );

  TextStyle get _rowStyle => const TextStyle(color: kTextColor);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        border: TableBorder.all(
          color: black,
          width: 3,
          borderRadius: BorderRadius.circular(5),
        ),
        decoration: const BoxDecoration(
          color: kPrimaryLight,
          borderRadius: BorderRadius.all(Radius.circular(5)),
        ),

        dividerThickness: 1,
        columns: [
          DataColumn(label: Text('Library', style: _titleStyle)),
          DataColumn(label: Text('Vulnerability', style: _titleStyle)),
          DataColumn(label: Text('Severity', style: _titleStyle)),
          DataColumn(label: Text('Fixed Version', style: _titleStyle)),
          DataColumn(
            label: Container(
              width: 300,
              alignment: Alignment.center,
              child: Text('Title', style: _titleStyle),
            ),
          ),
        ],
        rows:
            rows.map((row) {
              return DataRow(
                cells: [
                  DataCell(Text(row.library, style: _rowStyle)),
                  DataCell(Text(row.vulnerability, style: _rowStyle)),
                  DataCell(
                    Text(
                      row.severity,
                      style: _rowStyle.copyWith(
                        color: _getSeverityColor(row.severity),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  DataCell(Text(row.fixedVersion, style: _rowStyle)),
                  DataCell(
                    Container(
                      width: 350,
                      child: SingleChildScrollView(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Text(
                              row.title,
                              style: _rowStyle,
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              );
            }).toList(),
      ),
    );
  }

  Color _getSeverityColor(String severity) {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return kCriticalSeverity;
      case 'HIGH':
        return kHighSeverity;
      case 'MEDIUM':
        return kMediumSeverity;
      case 'LOW':
        return kLowSeverity;
      default:
        return Colors.grey;
    }
  }
}
