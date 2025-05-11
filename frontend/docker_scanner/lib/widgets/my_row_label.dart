import 'package:flutter/material.dart';

class MyRowLabel extends StatelessWidget {
  final String label;
  final Widget? rightChild;

  const MyRowLabel({
    super.key,
    required this.label,
    this.rightChild,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          label,
          style: const TextStyle(
            // fontFamily: 'JetBrainsMono',
            fontWeight: FontWeight.bold,
            fontSize: 18,
            color: Color(0xFF181C23),
          ),
        ),
        const Spacer(),
        if (rightChild != null) rightChild!,
      ],
    );
  }
}
