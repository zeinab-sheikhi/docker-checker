import 'package:flutter/material.dart';

class MyContainer extends StatelessWidget {
  final Widget child;
  final Color backgroundColor;
  final double? width;
  final double? height;
  final EdgeInsetsGeometry padding;
  final double borderRadius;
  final Offset boxShadowOffset;

  const MyContainer({
    super.key,
    required this.child,
    this.backgroundColor = const Color(0xFFFFF4DA),
    this.width,
    this.height,
    this.padding = const EdgeInsets.all(40),
    this.borderRadius = 15,
    this.boxShadowOffset = const Offset(8, 8),
  });
  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      padding: padding,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(borderRadius),
        border: Border.all(color: Colors.black, width: 4),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF181C23), // Dark shadow
            offset: boxShadowOffset,
            blurRadius: 0,
            spreadRadius: 0,
          ),
        ],
      ),
      child: child,
    );
  }
}
