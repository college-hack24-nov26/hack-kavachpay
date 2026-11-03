import 'package:flutter/material.dart';

/// Centralized color palette for KavachSetu – The Ghost Protocol.
/// All screens, components, buttons, badges, and surfaces MUST use these definitions.
class AppColors {
  AppColors._();

  // Brand Green Hierarchy
  static const Color brandGreen = Color(0xFF0B6B58);
  static const Color brandPressed = Color(0xFF095646);
  static const Color brandTint = Color(0xFFE6F2EE);

  // Surface & Neutral System
  static const Color background = Color(0xFFF4F3EF);
  static const Color card = Color(0xFFFFFFFF);
  static const Color cardSubtle = Color(0xFFFAF9F6);
  static const Color border = Color(0xFFE3E1DA);

  // Typography Palette
  static const Color textPrimary = Color(0xFF1C1F1D);
  static const Color textSecondary = Color(0xFF5F645F);
  static const Color textHint = Color(0xFF8A8E88);

  // Semantic States & Accompanying Tint Backgrounds
  static const Color success = Color(0xFF1E8E5A);
  static const Color successBg = Color(0xFFE3F4EA);

  static const Color warning = Color(0xFFB7791F);
  static const Color warningBg = Color(0xFFFDF3DC);

  static const Color danger = Color(0xFFC5382F);
  static const Color dangerBg = Color(0xFFFCE9E7);

  static const Color info = Color(0xFF2F63B5);
  static const Color infoBg = Color(0xFFE7EEF9);
}

