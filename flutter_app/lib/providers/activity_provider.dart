import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/activity.dart';
import 'auth_provider.dart';

final activityProvider = FutureProvider.autoDispose<List<ActivityModel>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getActivityHistory();
});

