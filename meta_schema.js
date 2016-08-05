var schemas;
if(!schemas) schemas = new jjv;
(function(){
	var my_meta_schema = {
    "id": "my_meta_schema",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "Core schema meta-schema",
    "definitions": {
        "schemaArray": {
            "type": "array",
            "minItems": 1,
            "items": { "$ref": "#" }
        },
		"schemaList": {
            "type": "object",
            "additionalProperties": { "$ref": "#" },
            "default": {}
        },
        "positiveInteger": {
            "type": "integer",
            "minimum": 0
        },
        "positiveIntegerDefault0": {
            "allOf": [ { "$ref": "#/definitions/positiveInteger" }, { "default": 0 } ]
        },
        "simpleTypes": {
            "enum": [ "null", "boolean", "integer", "number", "string", "array", "object" ]
        },
        "stringArray": {
            "type": "array",
            "items": { "type": "string" },
            "minItems": 1,
            "uniqueItems": true
        },
		//additions:
		"$data": {
			"type": "object",
			"required": [ "$data" ],
			"properties": {
				"$data": { "type": "string", "format": "relative-json-pointer" }
			},
			"additionalProperties": true
		}
    },
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "anyOf": [	{"format": "uri"}, {"format": "identifier"} ]
        },
        "$schema": {
            "type": "string",
            "anyOf": [	{"format": "uri"}, {"format": "identifier"} ]
        },
        "title": {
            "type": "string"
        },
        "description": {
            "type": "string"
        },
        "default": {},
        "multipleOf": { "oneOf": [
			{
				"type": "number",
				"minimum": 0,
				"exclusiveMinimum": true
			},
			{ "$ref": "#/definitions/$data" }//added
		]},
        "maximum": { "oneOf":[
			{ "type": "number" },
			{ "$ref": "#/definitions/$data" }//added
		]},
        "exclusiveMaximum": { "type": "boolean", "default": false },
        "minimum": { "oneOf": [
            { "type": "number" },
			{ "$ref": "#/definitions/$data" }//added
		]},
        "exclusiveMinimum": { "type": "boolean", "default": false },
        "maxLength": { "oneOf": [
			{ "$ref": "#/definitions/positiveInteger" },
			{ "$ref": "#/definitions/$data" }//added
		]},
        "minLength": { "oneOf": [
			{ "$ref": "#/definitions/positiveIntegerDefault0" },
			{ "$ref": "#/definitions/$data" }//added
		]},
        "pattern": { "oneOf": [
			{ "type": "string", "format": "regex" },
			{ "$ref": "#/definitions/$data" }//added
		]},
        "additionalItems": { "anyOf": [
                { "type": "boolean" },
                { "$ref": "#" }
            ],
            "default": {}
        },
        "items": { "anyOf": [
                { "$ref": "#" },
                { "$ref": "#/definitions/schemaArray" }
            ],
            "default": {}
        },
        "maxItems": { "oneOf": [
			{ "$ref": "#/definitions/positiveInteger" },
			{ "$ref": "#/definitions/$data" }//added
		]},
        "minItems": { "oneOf": [
			{ "$ref": "#/definitions/positiveIntegerDefault0" },
			{ "$ref": "#/definitions/$data" }//added
		]},
        "uniqueItems": { "oneOf": [
			{ "type": "boolean", "default": false },
			{ "$ref": "#/definitions/$data" }//added
		]},
        "maxProperties": { "oneOf": [
			{ "$ref": "#/definitions/positiveInteger" },
			{ "$ref": "#/definitions/$data" }//added
		]},
        "minProperties": { "oneOf": [
			{ "$ref": "#/definitions/positiveIntegerDefault0" },
			{ "$ref": "#/definitions/$data" }//added
		]},
        "required": { "$ref": "#/definitions/stringArray" },
        "additionalProperties": { "anyOf": [
                { "type": "boolean" },
                { "$ref": "#" }
            ],
            "default": {}
        },
        "definitions": { "$ref": "#/definitions/schemaList" },
        "properties": { "$ref": "#/definitions/schemaList" },
        "patternProperties": { "$ref": "#/definitions/schemaList" },
        "uniquePatternProperties": { "$ref": "#/definitions/schemaList" },
        "dependencies": {
            "type": "object",
            "additionalProperties": { "anyOf": [
				{ "$ref": "#" },
				{ "$ref": "#/definitions/stringArray" }
            ]}
        },
        "enum": { "oneOf": [
			{
				"type": "array",
				"minItems": 1,
				"uniqueItems": true
			},
			{ "$ref": "#/definitions/$data" }//added
		]},
        "type": { "anyOf": [
			{ "$ref": "#/definitions/simpleTypes" },
			{
				"type": "array",
				"items": { "$ref": "#/definitions/simpleTypes" },
				"minItems": 1,
				"uniqueItems": true
			}
        ]},
        "allOf": { "$ref": "#/definitions/schemaArray" },
        "anyOf": { "$ref": "#/definitions/schemaArray" },
        "oneOf": { "$ref": "#/definitions/schemaArray" },
        "not": { "$ref": "#" },
		// === additions ===
		"$ref": { "type":"string", "format":"json-reference" },
		"readOnly": { "oneOf": [
			{ "type": "boolean" },
			{ "$ref":"#/definitions/$data" }
		]},
		"constant": { },
		"isPropertyOf": { "oneOf": [
			{ "type": "string", "format": "relative-json-pointer" },
			{ "$ref":"#/definitions/$data" }
		]},
		"format": { "oneOf": [
			{ "type": "string", "enum": [
				"relative-json-pointer",
				"json-reference",
				"regex",
				"alpha",
				"alphanumeric",
				"identifier",
				"hexadecimal",
				"numeric",
				"date-time",
				"uppercase",
				"lowercase",
				"hostname",
				"uri",
				"email",
				"ipv4",
				"ipv6"
			]},
			{ "$ref":"#/definitions/$data" }
		]},
		"parseCoerce": { "type": "string" },
		"stringifyCoerce": { "type": "string" }
    },
    "additionalProperties": false, //modified
    "dependencies": {
        "exclusiveMaximum": [ "maximum" ],
        "exclusiveMinimum": [ "minimum" ],
		"properties": [ "additionalProperties" ], //modified
		"patternProperties": [ "additionalProperties" ], //modified
		"items": { "anyOf": [
			{
				"properties": {
					"items": { "type": "object" }
				},
				"additionalProperties": true
			},
			{
				"required": [ "items", "additionalItems" ],
				"properties": {
					"items": { "type": "array" }
				},
				"additionalProperties": true
			}
		]} //modified
    },
    "default": {}
};
	var res = schemas.addSchema('my_meta_schema',my_meta_schema).validate('my_meta_schema',my_meta_schema);
	if(res){
		console.dir(res);
		alert('мета-схема не валидна');
	}
})();
