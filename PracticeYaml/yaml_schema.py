from strictyaml import load, Map, scalar, Str, Int, Seq, YAMLError, Datetime, as_document, Bool, NullNone


schema = Map({"firstName": Str(),
              "dateOfBirth": Datetime(),
              "married": Bool(),
              "spouse": NullNone(),
              "children": Seq(Str())
              })
