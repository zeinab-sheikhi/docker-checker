import 'package:flutter/material.dart';
import '../consts.dart';

class MyRowLabel extends StatelessWidget {
  final String label;
  final Widget? rightChild;

  const MyRowLabel({super.key, required this.label, this.rightChild});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          label,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 18,
            color: kTextColor,
          ),
        ),
        const Spacer(),
        if (rightChild != null) rightChild!,
      ],
    );
  }
}
