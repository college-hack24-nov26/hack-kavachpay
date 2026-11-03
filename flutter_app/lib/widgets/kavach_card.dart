import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';

class KavachCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final VoidCallback? onTap;
  final Color backgroundColor;
  final BorderSide? border;

  const KavachCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
    this.onTap,
    this.backgroundColor = AppColors.card,
    this.border,
  });

  @override
  Widget build(BuildContext context) {
    final borderSide = border ?? const BorderSide(color: AppColors.border, width: 1);

    return Material(
      color: backgroundColor,
      borderRadius: BorderRadius.circular(16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: borderSide,
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        splashColor: AppColors.brandTint,
        highlightColor: AppColors.brandTint.withOpacity(0.5),
        child: Padding(
          padding: padding,
          child: child,
        ),
      ),
    );
  }
}

