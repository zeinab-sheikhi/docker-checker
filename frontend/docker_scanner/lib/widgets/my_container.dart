import 'package:flutter/material.dart';
import '../consts.dart'; // Import the consts file

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
    this.backgroundColor = kPrimaryLight, // Use kPrimaryLight
    this.width,
    this.height,
    this.padding = const EdgeInsets.all(40),
    this.borderRadius = 11,
    this.boxShadowOffset = const Offset(6, 6),
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
        border: Border.all(color: kButtonBorder, width: 4), // Use kButtonBorder
        boxShadow: [
          BoxShadow(
            color: kTextColor, // Use kTextColor for dark shadow
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
