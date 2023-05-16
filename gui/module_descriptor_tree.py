from gui.module_descriptor import ModuleDescriptor


descriptor = ModuleDescriptor({
    "type": "struct",
    "required": "Yes",
    "value": {
        "name":         ModuleDescriptor({"type": "str", "required": "Yes"}),
        "language":     ModuleDescriptor({"type": "str", "required": "Yes"}),

        # "module_type": ModuleDescriptor({"type": "str", "required": "No"}),
        # todo для module_class хочется так "required": "Yes If module_type == 'class' else No"
        "module_class": ModuleDescriptor({"type": "class", "required": "No"}),
        "entry_point": ModuleDescriptor({"type": "function", "required": "Yes"}),

        "description":  ModuleDescriptor({"type": "str", "required": "No"}),
        "input_ports":  ModuleDescriptor({
            "type": "array-struct",
            "required": "No",
            "value": ModuleDescriptor({
                "type": "struct",
                "required": "Yes",
                "value": {
                    "label": ModuleDescriptor({"type": "str", "required": "Yes"})
                }
            })
        }),
        "output_ports":  ModuleDescriptor({
            "type": "array-struct",
            "required": "No",
            "value": ModuleDescriptor({
                "type": "struct",
                "required": "Yes",
                "value": {
                    "label": ModuleDescriptor({"type": "str", "required": "Yes"})
                }
            })
        })
    }
})



