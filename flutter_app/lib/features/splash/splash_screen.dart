import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../core/constants/app_constants.dart';
import '../../widgets/kavach_button.dart';

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Spacer(),
              // Brand Icon & Badge
              Container(
                width: 68,
                height: 68,
                decoration: BoxDecoration(
                  color: AppColors.brandGreen,
                  borderRadius: BorderRadius.circular(18),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.brandGreen.withOpacity(0.18),
                      blurRadius: 16,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: const Center(
                  child: Icon(
                    Icons.shield_outlined,
                    color: Colors.white,
                    size: 34,
                  ),
                ),
              ),
              const SizedBox(height: 28),
              
              // App Name & Tagline
              Row(
                children: [
                  Text(
                    AppConstants.appName,
                    style: AppTypography.displayLarge.copyWith(fontSize: 32),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.brandTint,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      'STAGE 1',
                      style: AppTypography.caption.copyWith(
                        color: AppColors.brandGreen,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                AppConstants.appSubtitle.toUpperCase(),
                style: AppTypography.labelMedium.copyWith(
                  letterSpacing: 2.0,
                  color: AppColors.brandGreen,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                "Prove, Don't Share.",
                style: AppTypography.titleLarge.copyWith(
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'Next-generation privacy-first digital trust and financial verification. Verify financial eligibility and KYC predicates with zero unnecessary data exposure.',
                style: AppTypography.bodyMedium,
              ),

              const Spacer(),

              // Trust banner
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.card,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.border),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.lock_outline, size: 20, color: AppColors.brandGreen),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Ghost-Vault decoupled self-custodial credential architecture.',
                        style: AppTypography.caption.copyWith(color: AppColors.textSecondary),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Action buttons
              KavachButton(
                label: 'Get Started',
                onPressed: () => context.go('/login'),
              ),
              const SizedBox(height: 12),
              KavachButton(
                label: 'Sign In to Ghost-Vault',
                variant: ButtonVariant.secondary,
                onPressed: () => context.go('/login'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

