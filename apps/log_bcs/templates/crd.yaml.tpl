{% if is_old_version %}
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.6.1
  creationTimestamp: null
  name: bklogconfigs.bk.tencent.com
spec:
  group: bk.tencent.com
  names:
    kind: BkLogConfig
    listKind: BkLogConfigList
    plural: bklogconfigs
    singular: bklogconfig
  scope: Namespaced
  subresources:
    status: {}
  validation:
    openAPIV3Schema:
      description: BkLogConfig is the Schema for the bklogconfigs API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: BkLogConfigSpec defines the desired state of BkLogConfig
          properties:
            IgnoreOlder:
              type: string
            PackageCount:
              type: integer
            ScanFrequency:
              type: string
            allContainer:
              description: if set all_container is true will match all container
              type: boolean
            cleanInactive:
              type: string
            closeInactive:
              type: string
            containerNameMatch:
              items:
                type: string
              type: array
            dataId:
              description: Foo is an example field of BkLogConfig. Edit bklogconfig_types.go
                to remove/update
              format: int64
              type: integer
            encoding:
              type: string
            extMeta:
              additionalProperties:
                type: string
              type: object
            input:
              type: string
            labelSelector:
              description: A label selector is a label query over a set of resources.
                The result of matchLabels and matchExpressions are ANDed. An empty
                label selector matches all objects. A null label selector matches
                no objects.
              properties:
                matchExpressions:
                  description: matchExpressions is a list of label selector requirements.
                    The requirements are ANDed.
                  items:
                    description: A label selector requirement is a selector that contains
                      values, a key, and an operator that relates the key and values.
                    properties:
                      key:
                        description: key is the label key that the selector applies
                          to.
                        type: string
                      operator:
                        description: operator represents a key's relationship to a
                          set of values. Valid operators are In, NotIn, Exists and
                          DoesNotExist.
                        type: string
                      values:
                        description: values is an array of string values. If the operator
                          is In or NotIn, the values array must be non-empty. If the
                          operator is Exists or DoesNotExist, the values array must
                          be empty. This array is replaced during a strategic merge
                          patch.
                        items:
                          type: string
                        type: array
                    required:
                    - key
                    - operator
                    type: object
                  type: array
                matchLabels:
                  additionalProperties:
                    type: string
                  description: matchLabels is a map of {key,value} pairs. A single
                    {key,value} in the matchLabels map is equivalent to an element
                    of matchExpressions, whose key field is "key", the operator is
                    "In", and the values array contains only "value". The requirements
                    are ANDed.
                  type: object
              type: object
            multiline:
              description: MultilineConfig is bkunifylogbeat multiline options
              properties:
                maxLines:
                  type: integer
                pattern:
                  type: string
                timeout:
                  type: string
              type: object
            namespace:
              type: string
            logConfigType:
              description: match rule std_log_config,container_log_config,node_log_config
              type: string
            package:
              type: boolean
            path:
              items:
                type: string
              type: array
            workloadName:
              type: string
            workloadType:
              type: string
          required:
          - logConfigType
          type: object
        status:
          description: BkLogConfigStatus defines the observed state of BkLogConfig
          type: object
      type: object
  version: v1alpha1
  versions:
  - name: v1alpha1
    served: true
    storage: true
status:
  acceptedNames:
    kind: ""
    plural: ""
  conditions: []
  storedVersions: []

{% else %}
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.6.1
  creationTimestamp: null
  name: bklogconfigs.bk.tencent.com
spec:
  group: bk.tencent.com
  names:
    kind: BkLogConfig
    listKind: BkLogConfigList
    plural: bklogconfigs
    singular: bklogconfig
  scope: Namespaced
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        description: BkLogConfig is the Schema for the bklogconfigs API
        properties:
          apiVersion:
            description: 'APIVersion defines the versioned schema of this representation
              of an object. Servers should convert recognized schemas to the latest
              internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
            type: string
          kind:
            description: 'Kind is a string value representing the REST resource this
              object represents. Servers may infer this from the endpoint the client
              submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
            type: string
          metadata:
            type: object
          spec:
            description: BkLogConfigSpec defines the desired state of BkLogConfig
            properties:
              IgnoreOlder:
                type: string
              PackageCount:
                type: integer
              ScanFrequency:
                type: string
              allContainer:
                description: if set all_container is true will match all container
                type: boolean
              cleanInactive:
                type: string
              closeInactive:
                type: string
              containerNameMatch:
                items:
                  type: string
                type: array
              dataId:
                description: Foo is an example field of BkLogConfig. Edit bklogconfig_types.go
                  to remove/update
                format: int64
                type: integer
              encoding:
                type: string
              extMeta:
                additionalProperties:
                  type: string
                type: object
              input:
                type: string
              labelSelector:
                description: A label selector is a label query over a set of resources.
                  The result of matchLabels and matchExpressions are ANDed. An empty
                  label selector matches all objects. A null label selector matches
                  no objects.
                properties:
                  matchExpressions:
                    description: matchExpressions is a list of label selector requirements.
                      The requirements are ANDed.
                    items:
                      description: A label selector requirement is a selector that
                        contains values, a key, and an operator that relates the key
                        and values.
                      properties:
                        key:
                          description: key is the label key that the selector applies
                            to.
                          type: string
                        operator:
                          description: operator represents a key's relationship to
                            a set of values. Valid operators are In, NotIn, Exists
                            and DoesNotExist.
                          type: string
                        values:
                          description: values is an array of string values. If the
                            operator is In or NotIn, the values array must be non-empty.
                            If the operator is Exists or DoesNotExist, the values
                            array must be empty. This array is replaced during a strategic
                            merge patch.
                          items:
                            type: string
                          type: array
                      required:
                      - key
                      - operator
                      type: object
                    type: array
                  matchLabels:
                    additionalProperties:
                      type: string
                    description: matchLabels is a map of {key,value} pairs. A single
                      {key,value} in the matchLabels map is equivalent to an element
                      of matchExpressions, whose key field is "key", the operator
                      is "In", and the values array contains only "value". The requirements
                      are ANDed.
                    type: object
                type: object
              multiline:
                description: MultilineConfig is bkunifylogbeat multiline options
                properties:
                  maxLines:
                    type: integer
                  pattern:
                    type: string
                  timeout:
                    type: string
                type: object
              namespace:
                type: string
              logConfigType:
                description: match rule std_log_config,container_log_config,node_log_config
                type: string
              package:
                type: boolean
              path:
                items:
                  type: string
                type: array
              workloadName:
                type: string
              workloadType:
                type: string
            required:
            - logConfigType
            type: object
          status:
            description: BkLogConfigStatus defines the observed state of BkLogConfig
            type: object
        type: object
    served: true
    storage: true
    subresources:
      status: {}
status:
  acceptedNames:
    kind: ""
    plural: ""
  conditions: []
  storedVersions: []
{% endif %}