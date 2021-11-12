apiVersion: v1
kind: ServiceAccount
metadata:
  name: bk-log-sidecar
  namespace: {{ namespace }}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: bk-log-sidecar
  namespace: bk-log
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: bk-log-sidecar
subjects:
  - kind: ServiceAccount
    name: bk-log-sidecar
    namespace: {{ namespace }}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  creationTimestamp: null
  name: bk-log-sidecar
  namespace: {{ namespace }}
rules:
  - apiGroups:
      - bk.tencent.com
    resources:
      - bklogconfigs
    verbs:
      - create
      - delete
      - get
      - list
      - patch
      - update
      - watch
  - apiGroups:
      - bk.tencent.com
    resources:
      - bklogconfigs/finalizers
    verbs:
      - update
  - apiGroups:
      - bk.tencent.com
    resources:
      - bklogconfigs/status
    verbs:
      - get
      - patch
      - update
  - apiGroups:
      - ""
    resources:
      - pods
    verbs:
      - get
      - list
      - patch
      - update
      - watch
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: bk-log-bkunifylogbeat
  namespace: {{ namespace }}
data:
  bkunifylogbeat.conf: |
    ##################### bkunifylogbeat Configuration #############################
    #==================== Main ================================================
    logging.level: error
    output.bkpipe:
      endpoint: {{ gse_endpoint }}
    path.logs: /data/var/log/
    path.data: /data/var/lib/
    path.pid: /data/var/run/

    #==================== Registry ================================================
    registry.flush: "1s"
    queue:
      mem:
        events: 1024
        flush.min_events: 0
        flush.timeout: "1s"

    # monitoring reporter.
    xpack.monitoring.enabled: true
    xpack.monitoring.bkpipe:
      dataid: 1100006
      task_dataid: 1100007
      period: "30s"

    processors:
      - drop_event:
          when:
            not:
              has_fields: ["dataid"]

    #==================== bkunifylogbeat ================================================
    bkunifylogbeat.eventdataid: -1
    bkunifylogbeat.multi_config:
      - path: "/data/var/config/"
        file_pattern: "*.conf"
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: bkunifylogbeat-bklog
  namespace: {{ namespace }}
  labels:
    k8s-app: bkunifylogbeat-logging
spec:
  selector:
    matchLabels:
      name: bkunifylogbeat-bklog
  template:
    metadata:
      labels:
        name: bkunifylogbeat-bklog
    spec:
      tolerations:
        # this toleration is to have the daemonset runnable on master nodes
        # remove it if your masters can't run pods
        - key: node-role.kubernetes.io/master
          operator: Exists
          effect: NoSchedule
      shareProcessNamespace: true
      securityContext:
        runAsUser: 0
      containers:
        - name: bkunifylogbeat-bklog
          image: {{ bkunifylogbeat_image }}
          command:
            - /data/bin/bkunifylogbeat
            - -c
            - /etc/bk/bkunifylogbeat.conf
          resources:
            limits:
              memory: 200Mi
            requests:
              cpu: 100m
              memory: 200Mi
          volumeMounts:
            - name: host
              mountPath: {{ host_path }}
            - name: bk-log
              mountPath: /data/var/
            - name: bk-log-config
              mountPath: /data/var/config
            - name: config
              mountPath: /etc/bk/
            - name: timezone-config
              mountPath: /etc/localtime
        - name: bk-log-sidecar
          image: {{ bk_log_sidecar_image }}
          command:
            - /bk-log-sidecar
            - --docker-socket=unix:///var/host/var/run/docker.sock
            - --bkunifylogbeat-config=/data/config/
            - --bkunifylogbeat-pid-file=/data/run/bkunifylogbeat.pid
            - --host-path={{ host_path }}
          volumeMounts:
            - name: host
              mountPath: {{ host_path }}
              readOnly: true
            - name: bk-log
              mountPath: /data/
            - name: bk-log-config
              mountPath: /data/config
      serviceAccountName: "bk-log-sidecar"
      terminationGracePeriodSeconds: 30
      volumes:
        - name: bk-log
          hostPath:
            path: /var/bk/log/
        - name: bk-log-config
          emptyDir: {}
        - name: timezone-config
          hostPath:
            path: /etc/localtime
        - name: host
          hostPath:
            path: /
        - name: config
          configMap:
            name: bk-log-bkunifylogbeat