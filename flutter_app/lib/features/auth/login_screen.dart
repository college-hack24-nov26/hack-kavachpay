import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../core/constants/app_constants.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/kavach_button.dart';
import '../../widgets/kavach_text_field.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.disposeNavigator();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _autofillDemo() {
    _emailController.text = AppConstants.demoEmail;
    _passwordController.text = AppConstants.demoPassword;
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;
    
    final success = await ref.read(authProvider.notifier).login(
      _emailController.text.trim(),
      _passwordController.text,
    );

    if (success && mounted) {
      context.go('/dashboard');
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final isLoading = authState.status == AuthStatus.loading;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () => context.go('/'),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Access Ghost-Vault',
                  style: AppTypography.displayLarge.copyWith(fontSize: 26),
                ),
                const SizedBox(height: 6),
                Text(
                  'Sign in to manage and verify your decoupled credentials.',
                  style: AppTypography.bodyMedium,
                ),
                const SizedBox(height: 24),

                // Demo Autofill Helper Card
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: AppColors.brandTint,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.brandGreen.withOpacity(0.2)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.person_pin_outlined, color: AppColors.brandGreen),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Demo User: Aarav Mehta',
                              style: AppTypography.labelMedium.copyWith(color: AppColors.brandGreen),
                            ),
                            Text(
                              '${AppConstants.demoEmail}',
                              style: AppTypography.caption.copyWith(color: AppColors.brandPressed),
                            ),
                          ],
                        ),
                      ),
                      TextButton(
                        onPressed: _autofillDemo,
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 8),
                          minimumSize: Size.zero,
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        child: Text(
                          'Autofill',
                          style: AppTypography.labelMedium.copyWith(
                            color: AppColors.brandGreen,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                if (authState.errorMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: AppColors.dangerBg,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppColors.danger.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: AppColors.danger, size: 20),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            authState.errorMessage!,
                            style: AppTypography.caption.copyWith(color: AppColors.danger),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],

                KavachTextField(
                  controller: _emailController,
                  label: 'Email Address',
                  hint: 'e.g. user@kavachsetu.demo',
                  keyboardType: TextInputType.emailAddress,
                  prefixIcon: const Icon(Icons.mail_outline, size: 20, color: AppColors.textSecondary),
                  validator: (val) {
                    if (val == null || val.trim().isEmpty) return 'Email is required';
                    if (!val.contains('@')) return 'Enter a valid email address';
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                KavachTextField(
                  controller: _passwordController,
                  label: 'Password',
                  hint: 'Enter your account password',
                  obscureText: _obscurePassword,
                  prefixIcon: const Icon(Icons.lock_outline, size: 20, color: AppColors.textSecondary),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                      size: 20,
                      color: AppColors.textSecondary,
                    ),
                    onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                  ),
                  validator: (val) {
                    if (val == null || val.isEmpty) return 'Password is required';
                    return null;
                  },
                ),
                const SizedBox(height: 28),

                KavachButton(
                  label: 'Sign In',
                  isLoading: isLoading,
                  onPressed: _handleLogin,
                ),
                const SizedBox(height: 24),

                Center(
                  child: Text(
                    'Protected by Argon2id / Bcrypt credential salt\nZero plaintext credentials transmitted',
                    textAlign: TextAlign.center,
                    style: AppTypography.caption,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
extension on TextEditingController {
  void disposeNavigator() {}
}

