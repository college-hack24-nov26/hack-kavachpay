import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/dashboard_summary.dart';
import 'auth_provider.dart';

final dashboardFutureProvider = FutureProvider.autoDispose<DashboardSummaryModel>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getDashboardSummary();
});

