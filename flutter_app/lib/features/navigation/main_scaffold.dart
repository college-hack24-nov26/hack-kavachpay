import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';

class MainScaffold extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const MainScaffold({
    super.key,
    required this.navigationShell,
  });

  void _onTap(int index) {
    navigationShell.goBranch(
      index,
      initialLocation: index == navigationShell.currentIndex,
    );
  }

  @override
  Widget build(BuildContext context) {
    final currentIndex = navigationShell.currentIndex;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: navigationShell,
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: AppColors.card,
          border: Border(top: BorderSide(color: AppColors.border, width: 1)),
        ),
        child: SafeArea(
          child: NavigationBar(
            selectedIndex: currentIndex,
            onDestinationSelected: _onTap,
            backgroundColor: AppColors.card,
            indicatorColor: AppColors.brandTint,
            elevation: 0,
            height: 64,
            labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
            destinations: const [
              NavigationDestination(
                icon: Icon(Icons.dashboard_outlined, color: AppColors.textSecondary),
                selectedIcon: Icon(Icons.dashboard, color: AppColors.brandGreen),
                label: 'Home',
              ),
              NavigationDestination(
                icon: Icon(Icons.shield_outlined, color: AppColors.textSecondary),
                selectedIcon: Icon(Icons.shield, color: AppColors.brandGreen),
                label: 'Ghost-Vault',
              ),
              NavigationDestination(
                icon: Icon(Icons.history_outlined, color: AppColors.textSecondary),
                selectedIcon: Icon(Icons.history, color: AppColors.brandGreen),
                label: 'Activity',
              ),
              NavigationDestination(
                icon: Icon(Icons.settings_outlined, color: AppColors.textSecondary),
                selectedIcon: Icon(Icons.settings, color: AppColors.brandGreen),
                label: 'Settings',
              ),
            ],
          ),
        ),
      ),
    );
  }
}

