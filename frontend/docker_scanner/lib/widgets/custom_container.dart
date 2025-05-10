import 'package:flutter/material.dart';

class CustomContainer extends StatelessWidget {
  final Widget child;
  final Color backgroundColor;
  final double width;
  final EdgeInsetsGeometry padding;

  const CustomContainer({
    super.key,
    required this.child,
    this.backgroundColor = const Color(0xFFFFF4DA),
    this.width = 900,
    this.padding = const EdgeInsets.all(40),
  });
  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      padding: padding,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.black, width: 4),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF181C23), // Dark shadow
            offset: const Offset(8, 8),
            blurRadius: 0,
            spreadRadius: 0,
          ),
        ],
      ),
      child: child,
    );
  }
} 