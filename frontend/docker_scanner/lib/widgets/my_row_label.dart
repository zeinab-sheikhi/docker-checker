import 'package:flutter/material.dart';
import '../consts.dart';

class MyRowLabel extends StatelessWidget {
  final String label;
  final Widget? rightChild;
  final double fontSize;

  const MyRowLabel({
    super.key,
    required this.label,
    this.rightChild,
    this.fontSize = 20,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: fontSize,
            color: kTextColor,
          ),
        ),
        const Spacer(),
        if (rightChild != null) rightChild!,
      ],
    );
  }
}
