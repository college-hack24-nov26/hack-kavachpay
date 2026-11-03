class ActivityModel {
  final int id;
  final String actionType;
  final String title;
  final String? description;
  final String ipMasked;
  final String deviceInfo;
  final String timestamp;

  const ActivityModel({
    required this.id,
    required this.actionType,
    required this.title,
    this.description,
    required this.ipMasked,
    required this.deviceInfo,
    required this.timestamp,
  });

  factory ActivityModel.fromJson(Map<String, dynamic> json) {
    return ActivityModel(
      id: json['id'] ?? 0,
      actionType: json['action_type'] ?? '',
      title: json['title'] ?? '',
      description: json['description'],
      ipMasked: json['ip_masked'] ?? '',
      deviceInfo: json['device_info'] ?? '',
      timestamp: json['timestamp'] ?? '',
    );
  }
}

