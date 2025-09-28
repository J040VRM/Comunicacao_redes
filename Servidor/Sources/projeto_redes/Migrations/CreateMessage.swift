import Fluent

struct CreateMessage: AsyncMigration {
    func prepare(on database: any Database) async throws {
        try await database.schema("TB_Messages")
            .id()
            .field("client_ip", .string, .required)
            .field("message", .string, .required)
            .create()
    }

    func revert(on database: any Database) async throws {
        try await database.schema("TB_Messages").delete()
    }
}
